from __future__ import annotations

import shutil
import sys
from pathlib import Path

import geopandas as gpd
import pytest


REPOSITORY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "simulation_ui"))

from model_io import (  # noqa: E402
    ConfigurationError,
    RateSpec,
    export_configuration,
    load_crop_protection_document,
    read_run_parameters,
    read_scenario_metadata,
    resolve_field_column,
    validate_run_parameters,
)

sys.path.insert(0, str(REPOSITORY / "simulation_ui"))


def test_reads_single_field_run_parameters() -> None:
    parameters = read_run_parameters(REPOSITORY / "SingleField_Lindan_5feb.xrun")

    assert parameters["Project"] == "scenario/SingleField_100x100_dev"
    assert parameters["CropProtectionScenario"] == "xCP-SingleField_Lindan.xml"
    assert parameters["NumberMC"] == "3"


def test_reads_scenario_metadata() -> None:
    metadata = read_scenario_metadata(
        REPOSITORY, "scenario/SingleField_100x100_dev"
    )

    assert metadata.target_type == 2
    assert metadata.feature_id_attribute == "ID"
    assert metadata.start is not None
    assert metadata.start.isoformat() == "1979-01-01"


def test_allows_legacy_scenario_without_temporal_extent() -> None:
    metadata = read_scenario_metadata(REPOSITORY, "scenario/SingleField_100x100")

    assert metadata.name == "SingleField_100x100"
    assert metadata.start is None
    assert metadata.end is None


def test_loads_and_edits_present_demo_document() -> None:
    document = load_crop_protection_document(
        REPOSITORY, "xCP-SingleField_Lindan.xml"
    )
    application = document.applications()[0]

    document.update_application(
        application.id,
        target_crops="2",
        sequence_probability=1,
        products=["Lindan 2"],
        rates=[RateSpec(kind="uniform", lower=2000, upper=2400)],
        application_window="05-02 to 05-12",
        technology="Standard-Sprayer",
        in_crop_buffer=1.5,
        in_field_margin=2.5,
    )
    updated = document.applications()[0]

    assert updated.products == ["Lindan 2"]
    assert updated.rates[0].kind == "uniform"
    assert updated.rates[0].lower == 2000
    assert updated.application_window == "05-02 to 05-12"


def test_validates_active_substance_output_direction() -> None:
    document = load_crop_protection_document(
        REPOSITORY, "xCropProtection-demo-active-substance.xml"
    )
    parameters = read_run_parameters(REPOSITORY / "template.xrun")
    parameters["CropProtectionScenario"] = (
        "xCropProtection-demo-active-substance.xml"
    )

    errors = validate_run_parameters(REPOSITORY, parameters, document)

    assert any("cannot be converted back to product" in error for error in errors)


def test_rejects_invalid_choice_probabilities() -> None:
    document = load_crop_protection_document(REPOSITORY, "xCropProtection-demo.xml")
    parameters = read_run_parameters(REPOSITORY / "template.xrun")
    application = document.applications()[0]

    document.update_application(
        application.id,
        target_crops=application.target_crops,
        sequence_probability=0.6,
        products=application.products,
        rates=application.rates,
        application_window=application.application_window,
        technology=application.technology,
        in_crop_buffer=application.in_crop_buffer,
        in_field_margin=application.in_field_margin,
    )

    errors = validate_run_parameters(REPOSITORY, parameters, document)
    assert any("sum to 0.9" in error for error in errors)


def test_exports_non_destructive_run_bundle(tmp_path: Path) -> None:
    shutil.copytree(REPOSITORY / "CropProtection", tmp_path / "CropProtection")
    shutil.copytree(REPOSITORY / "scenario", tmp_path / "scenario")
    (tmp_path / "simulation_ui").mkdir()
    document = load_crop_protection_document(
        tmp_path, "xCP-SingleField_Lindan.xml"
    )
    parameters = read_run_parameters(REPOSITORY / "SingleField_Lindan_5feb.xrun")
    parameters["SimID"] = "ui-test-run"

    exported = export_configuration(tmp_path, parameters, document)

    assert exported.xrun_path.is_file()
    assert exported.crop_protection_path.is_file()
    written = read_run_parameters(exported.xrun_path)
    assert written["CropProtectionScenario"].startswith("generated/ui-test-run/")
    assert (
        tmp_path
        / "CropProtection"
        / "PPMCalendars"
        / "Simple_SingleField-calendar"
        / "PPMCalendar-SingleFieldLindan_1.xml"
    ).read_text(encoding="utf-8").startswith("<?xml")


def test_rejects_negative_probability() -> None:
    document = load_crop_protection_document(
        REPOSITORY, "xCP-SingleField_Lindan.xml"
    )
    application = document.applications()[0]

    with pytest.raises(ConfigurationError, match="between 0 and 1"):
        document.update_application(
            application.id,
            target_crops=application.target_crops,
            sequence_probability=-0.1,
            products=application.products,
            rates=application.rates,
            application_window=application.application_window,
            technology=application.technology,
            in_crop_buffer=application.in_crop_buffer,
            in_field_margin=application.in_field_margin,
        )


def test_rejects_reversed_uniform_rate_bounds() -> None:
    document = load_crop_protection_document(
        REPOSITORY, "xCP-SingleField_Lindan.xml"
    )
    application = document.applications()[0]

    with pytest.raises(ConfigurationError, match="0 <= Lower <= Upper"):
        document.update_application(
            application.id,
            target_crops=application.target_crops,
            sequence_probability=application.sequence_probability,
            products=application.products,
            rates=[RateSpec(kind="uniform", lower=2500, upper=2000)],
            application_window=application.application_window,
            technology=application.technology,
            in_crop_buffer=application.in_crop_buffer,
            in_field_margin=application.in_field_margin,
        )


def test_resolves_dbf_truncated_field_names() -> None:
    frame = gpd.GeoDataFrame({"LULCTypeI": [2], "ID": [1]})

    assert resolve_field_column(frame.columns, "LULCTypeId") == "LULCTypeI"
