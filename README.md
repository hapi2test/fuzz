# UAVConfigFuzzer

UAVConfigFuzzer explores PX4 configuration parameters using native setpoint generation and feedback-guided search. The repository also contains MAVLink scripts for simulator experiments and flight-log analysis.

## Repository Structure

```text
UAVConfigFuzzer/
  build_native.py          Build the native shared library from external PX4 sources
  requirements-build.txt   Compiler and plotting dependencies
  examples/                Configuration domains and example mission
  native/                  C++ generator, Auto adapter, and compatibility headers
  uavfuzz/
    __main__.py            Baseline estimation and 1-D / n-D search CLI
    backend.py             ctypes interface to the native generator
    model.py               Parameter domains, coordinates, and fitness metrics
    search.py              Feedback-guided search
    ablation.py            Five-strategy comparison
mavlink/                   Simulator parameter injection, mission execution, and ULog analysis
LICENSE
README.md
```

The former `DLL/`, `GArandom/`, `mutation/`, and `setpoint generator/` directories have been removed. The current software search workflow is under `UAVConfigFuzzer/`.

## Setup and Native Build

Use Python 3.10 or newer. A separate PX4-Autopilot source checkout is required; it is not included in this repository. The builder compiles PX4's `PositionSmoothing.cpp` and `VelocitySmoothing.cpp`, and extracts selected methods from `FlightTaskAuto.cpp` into an adapter. The supplied PX4 version must expose the interfaces expected by the adapter; compatibility with arbitrary PX4 revisions is not guaranteed.

Run the following from the repository root (Windows PowerShell):

```powershell
cd UAVConfigFuzzer
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-build.txt
python build_native.py --px4 "C:/path/to/PX4-Autopilot"
```

The build produces `build/setpoint.dll` on Windows or `build/libsetpoint.so` on other platforms, together with `build.log` and `provenance.json`. Provenance records source hashes, build settings, and the library hash.

On Linux, activate the environment with `source .venv/bin/activate`. The main CLI selects the platform-specific library name automatically; pass `--library build/libsetpoint.so` explicitly when using the ablation CLI on Linux.

## Configuration and Missions

- `examples/config.json` provides all 19 named defaults, discrete search domains, explicit correlation pairs, and generator settings. The current generator connects 15 parameters to auto-mission behavior.
- `MPC_ACC_HOR_MAX`, `MPC_TILTMAX_AIR`, `MPC_JERK_MAX`, and `MPC_TILTMAX_LND` remain in the defaults but are excluded from searchable domains.
- Search intervals, steps, and correlation pairs are explicit experiment inputs; the tool does not automatically extract constraints from PX4.
- `examples/mission.json` uses local north-east-down (NED) coordinates, where negative Z is above the origin, and includes takeoff, position, and landing waypoints. GPS missions are also accepted with `"frame": "gps"`.

## Run the Search

Run these commands from `UAVConfigFuzzer/` after building the library. Each output directory must be new; the CLI refuses to reuse an existing directory.

Estimate the default configuration's setpoint sequence and scores:

```powershell
python -m uavfuzz estimate --out runs/baseline
```

Run one-dimensional search, then use its bounds for correlated n-dimensional search:

```powershell
python -m uavfuzz 1d --out runs/search_1d --objective deviation --threshold 5 --n 20 --k 5 --iterations 10 --seed 42
python -m uavfuzz nd --single-bounds runs/search_1d/bounds.json --out runs/search_nd --objective deviation --threshold 5 --n 20 --k 5 --iterations 10 --seed 42
```

Both stages must use matching configuration, mission, and native-library provenance. Override inputs using `--config`, `--mission`, and `--library`.

Available objectives are:

| Objective | Implementation |
| --- | --- |
| `rapid` | Maximum absolute vertical acceleration in the generated samples |
| `deviation` | Maximum distance from a generated position to its target mission segment |
| `interruption` | Reciprocal minimum speed; infinite for incomplete sequences or zero minimum speed |

Startup and stopping samples contribute to the interruption score, so even a baseline may have an infinite score. A finite `--threshold` marks scores above the cutoff as software candidates; nonfinite runs are also candidates. Incomplete runs are automatically candidates when optimizing interruption.

## Compare Mutation Strategies

The ablation runner compares 1-D mutation, n-D mutation, genetic algorithm, binary search, and random mutation using a shared software oracle and equal native-evaluation budgets per method and seed:

```powershell
python -m uavfuzz.ablation --out runs/comparison --budget 600 --n 20 --k 5 --seeds 42
```

Random mutation changes one uniformly selected parameter at a time. The n-D budget includes its own 1-D warmup. The default oracle flags incomplete runs, vertical acceleration above 4 m/s², or deviation above 5 m; change these cutoffs with `--rapid-threshold` and `--deviation-threshold`. The runner rejects a baseline that already violates the chosen oracle. Binary search assumes a connected safe component and requires contiguous input intervals.

## Outputs and Interpretation

Baseline estimation writes `baseline.csv` and `manifest.json`. Search additionally writes:

| File | Contents |
| --- | --- |
| `trials.jsonl` | Evaluated configurations, statuses, and scores |
| `candidates.jsonl` | Software anomaly candidates |
| `best.json` | Retained search results |
| `bounds.json` | Remaining 1-D grid domains or conditional n-D results |
| `summary.json` | Trial count, candidate count, and elapsed time |

The ablation runner writes per-method, per-seed JSONL logs and `results.json`.

These are software setpoint experiments, not full vehicle simulation or flight validation. Remaining values are unexcluded grid points, not proven-safe configurations. The main n-D workflow retains anomalous combinations rather than projecting them onto independent parameter ranges. Ablation n-D/GA range summaries use conservative marginal exclusions and do not establish causality.

The project ignores local environments, build artifacts, run outputs, Python caches, figures, and tests through `UAVConfigFuzzer/.gitignore`; those directories are not supplied by the current upload.

## MAVLink Simulator Scripts

`mavlink/` contains a separate simulator workflow for configuration injection, mission execution, and ULog analysis. Its scripts contain environment-specific connection settings, log paths, and experiment values that must be adapted to your PX4 SITL setup. They are not automatically invoked by the software search CLI. The current `mavlink/main.py` entry point runs a local log-analysis example rather than launching a complete simulator experiment.

## Video Demo

We provide three videos showcasing three types of UAV anomalies caused by incorrect configurations.
* https://youtu.be/MfE_ELEV_GQ
* https://youtu.be/-i2bFYIB7O0
* https://youtu.be/4rUY63GKm9c

## License

This project is licensed under the [BSD 2-Clause License](LICENSE).
