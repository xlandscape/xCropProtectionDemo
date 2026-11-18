from __future__ import annotations

import copy
import datetime as dt
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


CPP_NAMESPACE = "urn:xCropProtectionLandscapeScenarioParametrization"
CPP = f"{{{CPP_NAMESPACE}}}"
XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
XSI = f"{{{XSI_NAMESPACE}}}"

ET.register_namespace("", CPP_NAMESPACE)
ET.register_namespace("xsi", XSI_NAMESPACE)

RUN_PARAMETER_NAMES = (
    "Modeller",
    "Project",
    "CropProtectionScenario",
    "OutputApplicationType",
    "ProductDatabase",
    "SimulationStart",
    "SimulationEnd",
    "SimID",
    "NumberMC",
    "ParallelProcesses",
    "MinimumAppliedArea",
)


class ConfigurationError(ValueError):
    pass


@dataclass
class ScenarioMetadata:
    project_path: str
    name: str
    description: str
    start: dt.date | None
    end: dt.date | None
    target_type: int
    shapefile: Path
    feature_id_attribute: str
    feature_type_attribute: str


@dataclass(frozen=True)
class RateSpec:
    kind: str
    value: float | None = None
    lower: float | None = None
    upper: float | None = None
    mean: float | None = None
    sd: float | None = None

    @classmethod
    def from_element(cls, element: ET.Element) -> "RateSpec":
        rate_type = element.get("type", "float")
        if rate_type == "float":
            return cls(kind="constant", value=_float(_text(element)))
        if rate_type.endswith("UniformDistribution"):
            return cls(
                kind="uniform",
                lower=_float(_child_text(element, "Lower")),
                upper=_float(_child_text(element, "Upper")),
            )
        if rate_type.endswith("NormalDistribution"):
            return cls(
                kind="normal",
                mean=_float(_child_text(element, "Mean")),
                sd=_float(_child_text(element, "SD")),
            )
        return cls(kind=rate_type, value=None)

    def append_to(self, parent: ET.Element) -> ET.Element:
        self.validate()
        element = ET.SubElement(
            parent,
            f"{CPP}ApplicationRate",
            {
                "type": self._type_name(),
                "unit": "g/ha",
                "scales": "global"
                if self.kind == "constant"
                else "time/year, space/base_geometry",
            },
        )
        if self.kind == "constant":
            element.text = _number_text(self.value)
        elif self.kind in {"uniform", "normal"}:
            for name, value in self._distribution_parameters():
                child = ET.SubElement(
                    element, f"{CPP}{name}", {"type": "float", "scales": "global"}
                )
                child.text = _number_text(value)
        else:
            raise ConfigurationError(f"Unsupported application-rate type: {self.kind}")
        return element

    def validate(self) -> None:
        if self.kind == "constant":
            if self.value is None or self.value < 0:
                raise ConfigurationError(
                    "Constant application rate must be zero or greater."
                )
        elif self.kind == "uniform":
            if (
                self.lower is None
                or self.upper is None
                or self.lower < 0
                or self.upper < 0
                or self.lower > self.upper
            ):
                raise ConfigurationError(
                    "Uniform application-rate bounds must satisfy 0 <= Lower <= Upper."
                )
        elif self.kind == "normal":
            if self.mean is None or self.mean < 0 or self.sd is None or self.sd < 0:
                raise ConfigurationError(
                    "Normal application rate requires a non-negative Mean and SD."
                )
        else:
            raise ConfigurationError(f"Unsupported application-rate type: {self.kind}")

    def _type_name(self) -> str:
        return {
            "constant": "float",
            "uniform": "xCropProtection.UniformDistribution",
            "normal": "xCropProtection.NormalDistribution",
        }.get(self.kind, self.kind)

    def _distribution_parameters(self) -> Iterable[tuple[str, float | None]]:
        if self.kind == "uniform":
            return (("Lower", self.lower), ("Upper", self.upper))
        if self.kind == "normal":
            return (("Mean", self.mean), ("SD", self.sd))
        return ()


@dataclass
class ApplicationView:
    id: str
    calendar_index: int
    calendar_path: str
    indication_index: int
    sequence_index: int
    application_index: int
    target_crops: str
    sequence_probability: float
    products: list[str]
    rates: list[RateSpec]
    input_scale: str
    application_window: str
    technology: str
    in_crop_buffer: float
    in_field_margin: float

    @property
    def label(self) -> str:
        products = " + ".join(self.products) or "(unnamed)"
        return (
            f"{products} | {self.target_crops} | "
            f"{Path(self.calendar_path).name} / sequence {self.sequence_index + 1}"
        )


@dataclass
class CalendarDocument:
    source_path: Path
    source_relative_path: str
    tree: ET.ElementTree


@dataclass
class TechnologyDefinition:
    name: str
    drift_reduction: float


@dataclass
class CropProtectionDocument:
    source_path: Path
    root_tree: ET.ElementTree
    crop_protection_dir: Path
    calendars: list[CalendarDocument]
    technologies: ET.Element

    def applications(self) -> list[ApplicationView]:
        views: list[ApplicationView] = []
        for calendar_index, document in enumerate(self.calendars):
            calendar_root = document.tree.getroot()
            target_crops = _child_text(calendar_root, "TargetCrops")
            indications = _child(calendar_root, "Indications")
            if indications is None:
                continue
            for indication_index, indication in enumerate(
                _children(indications, "Indication")
            ):
                for sequence_index, sequence in enumerate(
                    _children(indication, "ApplicationSequence")
                ):
                    probability = _float(sequence.get("probability"), 1.0)
                    for application_index, application in enumerate(
                        _children(sequence, "Application")
                    ):
                        tank = _require_child(application, "Tank")
                        products_element = _require_child(tank, "Products")
                        rate_container = _require_child(tank, "ApplicationRates")
                        products = _parse_list(_text(products_element))
                        rates = [
                            RateSpec.from_element(rate)
                            for rate in _children(rate_container, "ApplicationRate")
                        ]
                        if not products or len(products) != len(rates):
                            raise ConfigurationError(
                                f"{document.source_path.name} application "
                                f"{application_index + 1} must define one rate "
                                "for each product or active substance."
                            )
                        for rate in rates:
                            rate.validate()
                        view_id = "|".join(
                            str(value)
                            for value in (
                                calendar_index,
                                indication_index,
                                sequence_index,
                                application_index,
                            )
                        )
                        views.append(
                            ApplicationView(
                                id=view_id,
                                calendar_index=calendar_index,
                                calendar_path=document.source_relative_path,
                                indication_index=indication_index,
                                sequence_index=sequence_index,
                                application_index=application_index,
                                target_crops=target_crops,
                                sequence_probability=probability,
                                products=products,
                                rates=rates,
                                input_scale=products_element.get(
                                    "scales", "other/products"
                                ),
                                application_window=_child_text(
                                    application, "ApplicationWindow"
                                ),
                                technology=_child_text(application, "Technology"),
                                in_crop_buffer=_float(
                                    _child_text(application, "InCropBuffer")
                                ),
                                in_field_margin=_float(
                                    _child_text(application, "InFieldMargin")
                                ),
                            )
                        )
        return views

    def technology_definitions(self) -> list[TechnologyDefinition]:
        definitions = []
        for technology in _children(self.technologies, "Technology"):
            definitions.append(
                TechnologyDefinition(
                    name=_child_text(technology, "TechnologyName"),
                    drift_reduction=_float(
                        _child_text(technology, "DriftReduction")
                    ),
                )
            )
        return definitions

    def update_application(
        self,
        application_id: str,
        target_crops: str,
        sequence_probability: float,
        products: list[str],
        rates: list[RateSpec],
        application_window: str,
        technology: str,
        in_crop_buffer: float,
        in_field_margin: float,
    ) -> None:
        calendar_index, indication_index, sequence_index, application_index = (
            int(part) for part in application_id.split("|")
        )
        calendar_root = self.calendars[calendar_index].tree.getroot()
        indications = _require_child(calendar_root, "Indications")
        indication = _children(indications, "Indication")[indication_index]
        sequence = _children(indication, "ApplicationSequence")[sequence_index]
        application = _children(sequence, "Application")[application_index]

        if (
            not products
            or any(not product.strip() for product in products)
            or len(products) != len(rates)
        ):
            raise ConfigurationError(
                "Each product or active substance must have one application rate."
            )
        if not 0 <= sequence_probability <= 1:
            raise ConfigurationError("Sequence probability must be between 0 and 1.")
        if in_crop_buffer < 0 or in_field_margin < 0:
            raise ConfigurationError("Buffer and margin values cannot be negative.")
        for rate in rates:
            rate.validate()
        _validate_month_day_span(application_window)

        target_element = _require_child(calendar_root, "TargetCrops")
        target_element.text = _normalise_list(target_crops, int)
        sequence.set("probability", _number_text(sequence_probability))

        tank = _require_child(application, "Tank")
        products_element = _require_child(tank, "Products")
        products_element.text = " | ".join(product.strip() for product in products)
        rate_container = _require_child(tank, "ApplicationRates")
        rate_container.clear()
        rate_container.set("scales", products_element.get("scales", "other/products"))
        for rate in rates:
            rate.append_to(rate_container)

        _set_child_text(application, "ApplicationWindow", application_window)
        _set_child_text(application, "Technology", technology)
        _set_child_text(application, "InCropBuffer", _number_text(in_crop_buffer))
        _set_child_text(application, "InFieldMargin", _number_text(in_field_margin))

    def update_technology(self, name: str, drift_reduction: float) -> None:
        if not 0 <= drift_reduction <= 1:
            raise ConfigurationError("Drift reduction must be between 0 and 1.")
        for technology in _children(self.technologies, "Technology"):
            if _child_text(technology, "TechnologyName") == name:
                _set_child_text(
                    technology, "DriftReduction", _number_text(drift_reduction)
                )
                return
        raise ConfigurationError(f"Technology not found: {name}")


@dataclass(frozen=True)
class ExportedConfiguration:
    xrun_path: Path
    crop_protection_path: Path
    generated_directory: Path


def discover_run_templates(repository: Path) -> list[Path]:
    return sorted(path for path in repository.glob("*.xrun") if path.is_file())


def discover_scenarios(repository: Path) -> list[str]:
    scenario_dir = repository / "scenario"
    return sorted(
        path.parent.relative_to(repository).as_posix()
        for path in scenario_dir.glob("*/scenario.xproject")
    )


def discover_crop_protection_scenarios(repository: Path) -> list[str]:
    crop_protection_dir = repository / "CropProtection"
    return sorted(
        path.relative_to(crop_protection_dir).as_posix()
        for path in crop_protection_dir.glob("x*.xml")
        if path.is_file()
    )


def resolve_field_column(columns: Iterable[str], configured_name: str) -> str:
    column_names = [str(column) for column in columns]
    exact = next(
        (
            column
            for column in column_names
            if column.casefold() == configured_name.casefold()
        ),
        None,
    )
    if exact is not None:
        return exact
    prefix = configured_name[:10].casefold()
    matches = [
        column
        for column in column_names
        if column.casefold().startswith(prefix)
        or prefix.startswith(column.casefold())
    ]
    if len(matches) == 1:
        return matches[0]
    raise ConfigurationError(
        f"Configured field attribute '{configured_name}' was not found in the "
        f"shapefile columns: {', '.join(column_names)}"
    )


def read_run_parameters(path: Path) -> dict[str, str]:
    root = ET.parse(path).getroot()
    parameters = {
        child.tag: _text(child)
        for child in root
        if child.tag in RUN_PARAMETER_NAMES
    }
    missing = set(RUN_PARAMETER_NAMES) - parameters.keys()
    if missing:
        raise ConfigurationError(
            f"{path.name} is missing parameters: {', '.join(sorted(missing))}"
        )
    return parameters


def read_scenario_metadata(
    repository: Path, project_relative_path: str
) -> ScenarioMetadata:
    project_dir = _safe_repository_path(repository, project_relative_path)
    project_root = ET.parse(project_dir / "scenario.xproject").getroot()
    package_path = project_dir / "geo" / "package.xinfo"
    package_root = ET.parse(package_path).getroot()

    temporal = _find_descendant(project_root, "TemporalExtent")
    base = _require_descendant(package_root, "base")
    meta = _require_descendant(package_root, "meta")
    shapefile = package_path.parent / _child_text(base, "base_landscape_geometries")

    return ScenarioMetadata(
        project_path=project_relative_path,
        name=_child_text(project_root, "Name") or project_dir.name,
        description=_child_text(project_root, "Description"),
        start=(
            dt.date.fromisoformat(_child_text(temporal, "FromDate"))
            if temporal is not None and _child_text(temporal, "FromDate")
            else None
        ),
        end=(
            dt.date.fromisoformat(_child_text(temporal, "ToDate"))
            if temporal is not None and _child_text(temporal, "ToDate")
            else None
        ),
        target_type=int(_child_text(meta, "target_type")),
        shapefile=shapefile,
        feature_id_attribute=_child_text(base, "feature_id_attribute"),
        feature_type_attribute=_child_text(base, "feature_type_attribute"),
    )


def load_crop_protection_document(
    repository: Path, relative_path: str
) -> CropProtectionDocument:
    crop_protection_dir = repository / "CropProtection"
    source_path = _safe_repository_path(crop_protection_dir, relative_path)
    if source_path.suffix.lower() != ".xml":
        raise ConfigurationError("The browser UI currently supports XML scenarios.")

    root_tree = ET.parse(source_path)
    root = root_tree.getroot()
    calendar_parent = _require_child(root, "PPMCalendars")
    calendars: list[CalendarDocument] = []
    for calendar in _children(calendar_parent, "PPMCalendar"):
        include = calendar.get("include")
        if include:
            calendar_path = _safe_repository_path(crop_protection_dir, include)
            calendars.append(
                CalendarDocument(
                    source_path=calendar_path,
                    source_relative_path=calendar_path.relative_to(
                        crop_protection_dir
                    ).as_posix(),
                    tree=ET.parse(calendar_path),
                )
            )
        else:
            calendar_tree = ET.ElementTree(copy.deepcopy(calendar))
            calendars.append(
                CalendarDocument(
                    source_path=source_path,
                    source_relative_path=relative_path,
                    tree=calendar_tree,
                )
            )

    technologies_element = _require_child(root, "Technologies")
    technologies_include = technologies_element.get("include")
    if technologies_include:
        technologies_path = _safe_repository_path(
            crop_protection_dir, technologies_include
        )
        technologies = copy.deepcopy(ET.parse(technologies_path).getroot())
    else:
        technologies = copy.deepcopy(technologies_element)

    if not calendars:
        raise ConfigurationError(f"No PPM Calendars were found in {source_path.name}.")
    document = CropProtectionDocument(
        source_path=source_path,
        root_tree=root_tree,
        crop_protection_dir=crop_protection_dir,
        calendars=calendars,
        technologies=technologies,
    )
    if not document.applications():
        raise ConfigurationError(
            f"No applications were found in {source_path.name}'s PPM Calendars."
        )
    return document


def validate_run_parameters(
    repository: Path,
    parameters: Mapping[str, str],
    document: CropProtectionDocument,
) -> list[str]:
    errors: list[str] = []
    missing = [name for name in RUN_PARAMETER_NAMES if not str(parameters.get(name, "")).strip()]
    if missing:
        errors.append(f"Missing required values: {', '.join(missing)}")

    sim_id = str(parameters.get("SimID", ""))
    if sim_id and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", sim_id):
        errors.append(
            "SimID may contain letters, numbers, dots, underscores, and hyphens only."
        )

    if str(parameters.get("OutputApplicationType", "")) not in {
        "product",
        "active substance",
    }:
        errors.append("OutputApplicationType must be 'product' or 'active substance'.")

    try:
        start = dt.date.fromisoformat(str(parameters.get("SimulationStart", "")))
        end = dt.date.fromisoformat(str(parameters.get("SimulationEnd", "")))
        if start > end:
            errors.append("SimulationStart must be on or before SimulationEnd.")
    except ValueError:
        errors.append("Simulation dates must use the YYYY-MM-DD format.")

    for name in ("NumberMC", "ParallelProcesses"):
        try:
            if int(str(parameters.get(name, "0"))) <= 0:
                errors.append(f"{name} must be a positive integer.")
        except ValueError:
            errors.append(f"{name} must be a positive integer.")

    try:
        if float(str(parameters.get("MinimumAppliedArea", "-1"))) < 0:
            errors.append("MinimumAppliedArea cannot be negative.")
    except ValueError:
        errors.append("MinimumAppliedArea must be a number.")

    try:
        metadata = read_scenario_metadata(
            repository, str(parameters.get("Project", ""))
        )
        try:
            start = dt.date.fromisoformat(str(parameters.get("SimulationStart", "")))
            end = dt.date.fromisoformat(str(parameters.get("SimulationEnd", "")))
            if (
                metadata.start is not None
                and metadata.end is not None
                and (start < metadata.start or end > metadata.end)
            ):
                errors.append(
                    f"Simulation dates exceed the scenario range "
                    f"{metadata.start.isoformat()} to {metadata.end.isoformat()}."
                )
        except ValueError:
            pass
    except (ConfigurationError, FileNotFoundError, ET.ParseError, ValueError) as exc:
        errors.append(f"Scenario cannot be read: {exc}")

    try:
        _safe_repository_path(
            repository / "CropProtection",
            str(parameters.get("ProductDatabase", "")).replace(
                "CropProtection/", "", 1
            ),
        )
        if not (repository / str(parameters.get("ProductDatabase", ""))).is_file():
            errors.append("ProductDatabase does not point to an existing file.")
    except ConfigurationError as exc:
        errors.append(str(exc))

    if str(parameters.get("OutputApplicationType")) == "product":
        active_substance_apps = [
            app
            for app in document.applications()
            if app.input_scale == "other/active_substances"
        ]
        if active_substance_apps:
            errors.append(
                "Active-substance inputs cannot be converted back to product outputs."
            )

    for calendar in document.calendars:
        for indication in _descendants(calendar.tree.getroot(), "Indication"):
            if indication.get("type", "").endswith("ChoiceDistribution"):
                total = sum(
                    _float(sequence.get("probability"), 0.0)
                    for sequence in _children(indication, "ApplicationSequence")
                )
                if abs(total - 1.0) > 1e-9:
                    errors.append(
                        f"Choice probabilities in {calendar.source_path.name} "
                        f"sum to {_number_text(total)}, not 1."
                    )

    return errors


def export_configuration(
    repository: Path,
    parameters: Mapping[str, str],
    document: CropProtectionDocument,
) -> ExportedConfiguration:
    errors = validate_run_parameters(repository, parameters, document)
    if errors:
        raise ConfigurationError("\n".join(errors))

    sim_id = str(parameters["SimID"])
    generated_dir = repository / "simulation_ui" / "generated" / sim_id
    generated_cp_dir = repository / "CropProtection" / "generated" / sim_id
    calendar_dir = generated_cp_dir / "calendars"
    generated_dir.mkdir(parents=True, exist_ok=True)
    calendar_dir.mkdir(parents=True, exist_ok=True)

    calendar_includes: list[str] = []
    for index, calendar in enumerate(document.calendars):
        filename = f"{index + 1:02d}-{calendar.source_path.stem}.xml"
        calendar_path = calendar_dir / filename
        _write_xml(calendar.tree, calendar_path)
        calendar_includes.append(
            (Path("generated") / sim_id / "calendars" / filename).as_posix()
        )

    source_root = document.root_tree.getroot()
    exported_root = ET.Element(
        f"{CPP}xCropProtection",
        dict(source_root.attrib),
    )
    calendar_parent = ET.SubElement(exported_root, f"{CPP}PPMCalendars")
    for include in calendar_includes:
        ET.SubElement(
            calendar_parent, f"{CPP}PPMCalendar", {"include": include}
        )
    technologies_parent = ET.SubElement(exported_root, f"{CPP}Technologies")
    for technology in _children(document.technologies, "Technology"):
        technologies_parent.append(copy.deepcopy(technology))

    crop_protection_path = generated_cp_dir / "xCropProtection.xml"
    _write_xml(ET.ElementTree(exported_root), crop_protection_path)

    exported_parameters = dict(parameters)
    exported_parameters["CropProtectionScenario"] = (
        crop_protection_path.relative_to(repository / "CropProtection").as_posix()
    )
    xrun_path = generated_dir / f"{sim_id}.xrun"
    write_run_parameters(xrun_path, exported_parameters)

    return ExportedConfiguration(
        xrun_path=xrun_path,
        crop_protection_path=crop_protection_path,
        generated_directory=generated_dir,
    )


def write_run_parameters(path: Path, parameters: Mapping[str, str]) -> Path:
    root = ET.Element("Parameters")
    for name in RUN_PARAMETER_NAMES:
        if name not in parameters:
            raise ConfigurationError(f"Missing parameter: {name}")
        ET.SubElement(root, name).text = str(parameters[name])
    ET.ElementTree(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_xml(ET.ElementTree(root), path)
    return path


def runtime_command(repository: Path) -> list[str] | None:
    python_path = repository / "model" / "core" / "bin" / "python-3.9.7-amd64" / "python.exe"
    init_path = repository / "model" / "core" / "init.py"
    if not python_path.is_file() or not init_path.is_file():
        return None
    return [str(python_path), "-u", str(init_path)]


def run_output_directory(repository: Path, sim_id: str) -> Path:
    return repository / "run" / sim_id


def start_simulation(
    repository: Path, xrun_path: Path, sim_id: str
) -> tuple[subprocess.Popen[Any], Path]:
    command = runtime_command(repository)
    if command is None:
        raise ConfigurationError(
            "The Landscape Model runtime is unavailable. Initialise the model/core "
            "submodule before launching a simulation."
        )
    output_dir = run_output_directory(repository, sim_id)
    if output_dir.exists():
        raise ConfigurationError(
            f"The SimID '{sim_id}' already exists under run/. Choose a new SimID."
        )
    log_path = xrun_path.parent / f"{sim_id}.runtime.log"
    log_file = log_path.open("w", encoding="utf-8")
    try:
        process = subprocess.Popen(
            [*command, str(xrun_path)],
            cwd=repository,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    finally:
        log_file.close()
    return process, log_path


def _safe_repository_path(base: Path, relative: str) -> Path:
    if not relative:
        raise ConfigurationError("A relative path is required.")
    candidate = (base / relative.replace("\\", os.sep)).resolve()
    resolved_base = base.resolve()
    try:
        candidate.relative_to(resolved_base)
    except ValueError as exc:
        raise ConfigurationError(
            f"Path leaves the expected repository directory: {relative}"
        ) from exc
    if not candidate.exists():
        raise ConfigurationError(f"File or directory does not exist: {relative}")
    return candidate


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _children(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in element if _local_name(child.tag) == name]


def _child(element: ET.Element, name: str) -> ET.Element | None:
    return next((child for child in element if _local_name(child.tag) == name), None)


def _require_child(element: ET.Element, name: str) -> ET.Element:
    found = _child(element, name)
    if found is None:
        raise ConfigurationError(f"Required element '{name}' was not found.")
    return found


def _descendants(element: ET.Element, name: str) -> Iterable[ET.Element]:
    return (child for child in element.iter() if _local_name(child.tag) == name)


def _require_descendant(element: ET.Element, name: str) -> ET.Element:
    found = _find_descendant(element, name)
    if found is None:
        raise ConfigurationError(f"Required element '{name}' was not found.")
    return found


def _find_descendant(element: ET.Element, name: str) -> ET.Element | None:
    return next(
        (child for child in element.iter() if _local_name(child.tag) == name), None
    )


def _text(element: ET.Element | None) -> str:
    return (element.text or "").strip() if element is not None else ""


def _child_text(element: ET.Element, name: str) -> str:
    return _text(_child(element, name))


def _set_child_text(element: ET.Element, name: str, value: str) -> None:
    _require_child(element, name).text = value


def _float(value: str | None, default: float | None = None) -> float:
    try:
        return float(value or "")
    except ValueError as exc:
        if default is not None:
            return default
        raise ConfigurationError(f"Expected a number, got: {value!r}") from exc


def _number_text(value: float | None) -> str:
    if value is None:
        raise ConfigurationError("A numeric distribution parameter is missing.")
    return f"{value:.12g}"


def _parse_list(value: str) -> list[str]:
    return [item.strip() for item in value.replace("|", "\n").splitlines() if item.strip()]


def _normalise_list(value: str, item_type: type[int]) -> str:
    items = [part for part in re.split(r"[\s,|]+", value.strip()) if part]
    if not items:
        raise ConfigurationError("At least one target crop is required.")
    try:
        return " ".join(str(item_type(item)) for item in items)
    except ValueError as exc:
        raise ConfigurationError("Target crops must be integers.") from exc


def _validate_month_day_span(value: str) -> None:
    match = re.fullmatch(r"\s*(\d{2})-(\d{2})\s+to\s+(\d{2})-(\d{2})\s*", value)
    if not match:
        raise ConfigurationError(
            "ApplicationWindow must use the format MM-DD to MM-DD."
        )
    dt.datetime.strptime(f"2000-{match.group(1)}-{match.group(2)}", "%Y-%m-%d")
    dt.datetime.strptime(f"2000-{match.group(3)}-{match.group(4)}", "%Y-%m-%d")


def _write_xml(tree: ET.ElementTree, path: Path) -> None:
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)
