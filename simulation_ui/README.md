# xCropProtection simulation studio

This Streamlit interface parameterises XML-based simulations in the current
`xCropProtectionDemo` repository. It reads the model's existing `.xrun`, landscape,
PPM calendar, and technology files, validates the resulting values, and writes a
non-destructive run bundle.

## Start

From the repository root:

```powershell
python -m pip install -r simulation_ui\requirements.txt
Dashboard_start.bat
```

The browser UI opens at `http://localhost:8501`.

Stop the dashboard with:

```powershell
Dashboard_stop.bat
```

The wrappers use `.venv\Scripts\python.exe` when available and otherwise fall
back to `python` from `PATH`. Additional Streamlit arguments can be passed to
`Dashboard_start.bat`.

## Supported workflow

1. Select an existing `.xrun` template, landscape scenario, and XML crop-protection
   scenario.
2. Edit experiment dates, output type, Monte Carlo settings, and minimum applied
   area.
3. Select an application and edit its target crop, sequence probability, product
   or active substance, rate (constant/uniform/normal), window, technology, buffer,
   and margin.
4. Adjust drift-reduction technology definitions.
5. Create a validated run bundle.
6. Launch it when the `model/core` submodule is initialised.

Generated files are placed below:

- `simulation_ui/generated/<SimID>/<SimID>.xrun`
- `CropProtection/generated/<SimID>/`

The source parameterisation files and existing scenarios are not overwritten. Run
bundles require a unique `SimID` because the model stores results in
`run/<SimID>`.

## Notes

- XML crop-protection parameterisations are supported. The legacy Excel parser
  remains available through `template-simple-parser.xrun`.
- A tank mixture can be edited one tank item at a time.
- `SimulationStart` and `SimulationEnd` are checked against scenario metadata.
- Active-substance input is rejected when the configured output is `product`.
