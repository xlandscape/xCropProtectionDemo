from __future__ import annotations

import datetime as dt
from pathlib import Path

import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium

from model_io import (
    ConfigurationError,
    RateSpec,
    discover_crop_protection_scenarios,
    discover_run_templates,
    discover_scenarios,
    export_configuration,
    load_crop_protection_document,
    read_run_parameters,
    read_scenario_metadata,
    resolve_field_column,
    run_output_directory,
    runtime_command,
    start_simulation,
    validate_run_parameters,
)


REPOSITORY = Path(__file__).resolve().parents[1]


@st.cache_data
def option_index(options: list[str], current: str) -> int:
    return options.index(current) if current in options else 0


@st.cache_data
def field_count(shapefile: Path) -> int:
    return len(gpd.read_file(shapefile))


@st.cache_data
def load_fields(shapefile: Path) -> gpd.GeoDataFrame:
    frame = gpd.read_file(shapefile)
    return frame.to_crs(4326) if frame.crs else frame


st.set_page_config(
    page_title="xCropProtection parameterisation",
    page_icon="🌱",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp { background: #f5f7f8; }
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #dce4e7;
        border-radius: 10px;
        padding: 12px 16px;
    }
    .xcp-callout {
        background: #e8f4f1;
        border-left: 5px solid #1e756d;
        padding: 12px 16px;
        border-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("xCropProtection simulation studio")
st.caption(
    "Configure landscape, treatment, variability, and Monte Carlo parameters for "
    "the model shipped in this repository."
)

templates = discover_run_templates(REPOSITORY)
scenario_options = discover_scenarios(REPOSITORY)
crop_options = discover_crop_protection_scenarios(REPOSITORY)
if not templates:
    st.error("No .xrun templates were found in the repository root.")
    st.stop()

with st.sidebar:
    st.header("Source configuration")
    default_template = "SingleField_Lindan_5feb.xrun"
    default_index = (
        [path.name for path in templates].index(default_template)
        if default_template in [path.name for path in templates]
        else 0
    )
    template_name = st.selectbox(
        "XRUN template",
        options=[path.name for path in templates],
        index=default_index,
        help="Used as the starting point; it is never overwritten.",
    )
    template_path = REPOSITORY / template_name
    template_parameters = read_run_parameters(template_path)

    st.divider()
    st.subheader("Model parameterisation")
    selected_project = st.selectbox(
        "Landscape scenario",
        options=scenario_options,
        index=option_index(scenario_options, template_parameters["Project"]),
    )
    selected_crop_scenario = st.selectbox(
        "Crop protection scenario",
        options=crop_options,
        index=option_index(
            crop_options, template_parameters["CropProtectionScenario"]
        ),
    )
    st.info(
        "Exports go to simulation_ui/generated/<SimID> and "
        "CropProtection/generated/<SimID>. Original examples remain unchanged."
    )

model_key = selected_crop_scenario
if st.session_state.get("loaded_model_key") != model_key:
    try:
        st.session_state["crop_document"] = load_crop_protection_document(
            REPOSITORY, selected_crop_scenario
        )
        st.session_state["loaded_model_key"] = model_key
        st.session_state.pop("exported", None)
    except ConfigurationError as exc:
        st.error(str(exc))
        st.stop()

document = st.session_state["crop_document"]
metadata = read_scenario_metadata(REPOSITORY, selected_project)
applications = document.applications()

metric_columns = st.columns(4)
metric_columns[0].metric("Landscape fields", field_count(metadata.shapefile))
metric_columns[1].metric("PPM calendars", len(document.calendars))
metric_columns[2].metric("Applications", len(applications))
metric_columns[3].metric("Target crop type", metadata.target_type)

global_tab, treatment_tab, landscape_tab, export_tab = st.tabs(
    ["Simulation", "Treatments", "Landscape", "Review & run"]
)

with global_tab:
    st.subheader("Experiment parameters")
    st.markdown(
        '<div class="xcp-callout">These values correspond to the parameters in the '
        'selected <code>.xrun</code> file.</div>',
        unsafe_allow_html=True,
    )
    date_constraints = {}
    if metadata.start is not None:
        date_constraints["min_value"] = metadata.start
    if metadata.end is not None:
        date_constraints["max_value"] = metadata.end
    with st.form("run_parameters"):
        left, right = st.columns(2)
        modeller = left.text_input(
            "Modeller",
            value=template_parameters["Modeller"],
        )
        sim_id = left.text_input(
            "Simulation ID",
            value=st.session_state.get("sim_id", template_parameters["SimID"]),
            help="A unique identifier; the model creates run/<SimID>.",
        )
        start_date = left.date_input(
            "Simulation start",
            value=dt.date.fromisoformat(template_parameters["SimulationStart"]),
            **date_constraints,
        )
        end_date = left.date_input(
            "Simulation end",
            value=dt.date.fromisoformat(template_parameters["SimulationEnd"]),
            **date_constraints,
        )
        output_type = right.selectbox(
            "Output application type",
            ["product", "active substance"],
            index=["product", "active substance"].index(
                template_parameters["OutputApplicationType"]
            ),
        )
        product_database = right.text_input(
            "Product database",
            value=template_parameters["ProductDatabase"],
        )
        number_mc = right.number_input(
            "Monte Carlo runs",
            min_value=1,
            value=int(template_parameters["NumberMC"]),
            step=1,
        )
        parallel_processes = right.number_input(
            "Parallel processes",
            min_value=1,
            value=int(template_parameters["ParallelProcesses"]),
            step=1,
        )
        minimum_area = right.number_input(
            "Minimum applied area [m²]",
            min_value=0.0,
            value=float(template_parameters["MinimumAppliedArea"]),
            step=1.0,
        )
        if metadata.start is not None and metadata.end is not None:
            st.caption(
                f"Scenario validity: {metadata.start.isoformat()} to "
                f"{metadata.end.isoformat()}."
            )
        else:
            st.caption("This scenario does not declare a temporal extent.")
        applied = st.form_submit_button(
            "Apply simulation parameters", type="primary", width="stretch"
        )
    if applied:
        st.session_state["parameters"] = {
            "Modeller": modeller,
            "Project": selected_project,
            "CropProtectionScenario": selected_crop_scenario,
            "OutputApplicationType": output_type,
            "ProductDatabase": product_database,
            "SimulationStart": start_date.isoformat(),
            "SimulationEnd": end_date.isoformat(),
            "SimID": sim_id,
            "NumberMC": str(number_mc),
            "ParallelProcesses": str(parallel_processes),
            "MinimumAppliedArea": str(minimum_area),
        }
        st.session_state["sim_id"] = sim_id
        st.success("Simulation parameters applied to the export draft.")

with treatment_tab:
    st.subheader("PPM calendars and applications")
    selected_application_id = st.selectbox(
        "Application",
        options=[application.id for application in applications],
        format_func=lambda application_id: next(
            application.label
            for application in applications
            if application.id == application_id
        ),
    )
    selected = next(
        application
        for application in applications
        if application.id == selected_application_id
    )
    tank_index = st.selectbox(
        "Tank item",
        options=list(range(len(selected.products))),
        format_func=lambda index: (
            f"{index + 1}: {selected.products[index]}"
            if index < len(selected.products)
            else str(index + 1)
        ),
        help="Tank mixtures contain more than one product or active substance.",
    )
    selected_rate = selected.rates[tank_index]
    technologies = [technology.name for technology in document.technology_definitions()]

    with st.form("application_editor"):
        identity_left, identity_right = st.columns(2)
        target_crops = identity_left.text_input(
            "Target crop IDs",
            value=selected.target_crops,
            help="Space- or comma-separated LULC type identifiers.",
        )
        probability = identity_right.number_input(
            "Application-sequence probability",
            min_value=0.0,
            max_value=1.0,
            value=float(selected.sequence_probability),
            step=0.01,
            help="All alternative sequences in one indication must sum to 1.",
        )
        product_name = identity_left.text_input(
            "Product / active substance name",
            value=selected.products[tank_index],
        )
        rate_mode = identity_right.selectbox(
            "Application-rate definition",
            ["constant", "uniform", "normal"],
            index=["constant", "uniform", "normal"].index(
                selected_rate.kind
                if selected_rate.kind in {"constant", "uniform", "normal"}
                else "constant"
            ),
        )

        rate_left, rate_right = st.columns(2)
        constant_rate = rate_left.number_input(
            "Constant rate [g/ha]",
            min_value=0.0,
            value=float(selected_rate.value or selected_rate.mean or 0.0),
            disabled=rate_mode != "constant",
        )
        lower = rate_left.number_input(
            "Uniform lower [g/ha]",
            min_value=0.0,
            value=float(selected_rate.lower or selected_rate.value or 0.0),
            disabled=rate_mode != "uniform",
        )
        upper = rate_right.number_input(
            "Uniform upper [g/ha]",
            min_value=0.0,
            value=float(selected_rate.upper or selected_rate.value or 0.0),
            disabled=rate_mode != "uniform",
        )
        mean = rate_left.number_input(
            "Normal mean [g/ha]",
            min_value=0.0,
            value=float(selected_rate.mean or selected_rate.value or 0.0),
            disabled=rate_mode != "normal",
        )
        sd = rate_right.number_input(
            "Normal SD [g/ha]",
            min_value=0.0,
            value=float(selected_rate.sd or 0.0),
            disabled=rate_mode != "normal",
        )
        application_window = identity_left.text_input(
            "Application window",
            value=selected.application_window,
            help="Format: MM-DD to MM-DD",
        )
        technology = identity_right.selectbox(
            "Application technology",
            technologies,
            index=technologies.index(selected.technology)
            if selected.technology in technologies
            else 0,
        )
        in_crop_buffer = identity_left.number_input(
            "In-crop buffer [m]",
            min_value=0.0,
            value=float(selected.in_crop_buffer),
        )
        in_field_margin = identity_right.number_input(
            "In-field margin [m]",
            min_value=0.0,
            value=float(selected.in_field_margin),
        )
        treatment_applied = st.form_submit_button(
            "Apply treatment changes", type="primary", width="stretch"
        )

    if treatment_applied:
        rate = RateSpec(
            kind=rate_mode,
            value=constant_rate if rate_mode == "constant" else None,
            lower=lower if rate_mode == "uniform" else None,
            upper=upper if rate_mode == "uniform" else None,
            mean=mean if rate_mode == "normal" else None,
            sd=sd if rate_mode == "normal" else None,
        )
        products = list(selected.products)
        rates = list(selected.rates)
        products[tank_index] = product_name.strip()
        rates[tank_index] = rate
        try:
            document.update_application(
                application_id=selected.id,
                target_crops=target_crops,
                sequence_probability=probability,
                products=products,
                rates=rates,
                application_window=application_window,
                technology=technology,
                in_crop_buffer=in_crop_buffer,
                in_field_margin=in_field_margin,
            )
            st.session_state.pop("exported", None)
            st.success("Treatment changes applied to the export draft.")
        except (ConfigurationError, ValueError) as exc:
            st.error(str(exc))

    st.divider()
    st.subheader("Technology definitions")
    technology_defs = document.technology_definitions()
    technology_name = st.selectbox(
        "Edit technology",
        [definition.name for definition in technology_defs],
        key="technology_name",
    )
    drift_definition = next(
        definition
        for definition in technology_defs
        if definition.name == technology_name
    )
    drift_reduction = st.slider(
        "Drift reduction fraction",
        min_value=0.0,
        max_value=1.0,
        value=float(drift_definition.drift_reduction),
        step=0.01,
    )
    if st.button("Apply technology change"):
        document.update_technology(technology_name, drift_reduction)
        st.session_state.pop("exported", None)
        st.success("Technology change applied to the export draft.")

with landscape_tab:
    st.subheader(metadata.name)
    st.write(metadata.description)
    st.caption(
        f"Feature ID: {metadata.feature_id_attribute} | "
        f"Land-cover ID: {metadata.feature_type_attribute} | "
        f"Simulation range: {metadata.start or 'unspecified'} to "
        f"{metadata.end or 'unspecified'}"
    )
    field_data = load_fields(metadata.shapefile)
    feature_id_column = resolve_field_column(
        field_data.columns, metadata.feature_id_attribute
    )
    feature_type_column = resolve_field_column(
        field_data.columns, metadata.feature_type_attribute
    )
    st_folium(
        field_data.explore(
            column=feature_type_column,
            tooltip=[feature_id_column, feature_type_column],
            tiles="OpenStreetMap",
            legend=True,
        ),
        use_container_width=True,
        height=520,
    )

with export_tab:
    st.subheader("Review and export")
    parameters = st.session_state.get("parameters")
    if parameters is None:
        st.warning("Apply the Simulation parameters before exporting.")
    else:
        parameters = {
            **parameters,
            "Project": selected_project,
            "CropProtectionScenario": selected_crop_scenario,
        }
        errors = validate_run_parameters(REPOSITORY, parameters, document)
        summary_left, summary_right = st.columns(2)
        with summary_left:
            st.markdown("#### Run")
            st.json(parameters)
        with summary_right:
            st.markdown("#### Parameterisation")
            for application in document.applications():
                st.write(
                    f"• **{' + '.join(application.products)}** — "
                    f"{application.application_window}, crop "
                    f"{application.target_crops}, "
                    f"{application.technology}"
                )
        if errors:
            for error in errors:
                st.error(error)
        else:
            st.success("The configuration passed repository-level validation.")

        if st.button(
            "Create run bundle",
            type="primary",
            width="stretch",
            disabled=bool(errors),
        ):
            try:
                exported = export_configuration(REPOSITORY, parameters, document)
                st.session_state["exported"] = exported
            except ConfigurationError as exc:
                st.error(str(exc))

    exported = st.session_state.get("exported")
    if exported is not None:
        st.success(f"Created {exported.xrun_path.name}.")
        st.code(str(exported.xrun_path))
        st.code(str(exported.crop_protection_path))
        with exported.xrun_path.open(encoding="utf-8") as xrun_file:
            st.download_button(
                "Download .xrun file",
                data=xrun_file.read(),
                file_name=exported.xrun_path.name,
                mime="application/xml",
            )

        command = runtime_command(REPOSITORY)
        if command is None:
            st.warning(
                "The run bundle is ready, but the bundled Landscape Model runtime is "
                "not available in this checkout. Initialise the model/core submodule "
                "and restart the UI before launching."
            )
        else:
            existing_output = run_output_directory(
                REPOSITORY, parameters["SimID"]
            )
            if st.button(
                "Launch simulation",
                type="primary",
                disabled=existing_output.exists(),
                width="stretch",
            ):
                try:
                    process, log_path = start_simulation(
                        REPOSITORY,
                        exported.xrun_path,
                        parameters["SimID"],
                    )
                    st.session_state["runtime_log"] = log_path
                    st.success(f"Simulation started (process {process.pid}).")
                except ConfigurationError as exc:
                    st.error(str(exc))

        runtime_log = st.session_state.get("runtime_log")
        if runtime_log is not None and runtime_log.is_file():
            st.caption(f"Runtime log: {runtime_log}")
            st.code(runtime_log.read_text(encoding="utf-8")[-12000:])
