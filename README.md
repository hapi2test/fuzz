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

## Setup

Use Python 3.10 or newer. 
A separate PX4-Autopilot source checkout is required (v1.15.0). 
The builder compiles PX4's `PositionSmoothing.cpp` and `VelocitySmoothing.cpp`, and extracts selected methods from `FlightTaskAuto.cpp` into an adapter. 

Run the following from the repository root:

```powershell
cd UAVConfigFuzzer
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-build.txt
python build_native.py --px4 "C:/path/to/PX4-Autopilot"
```


## Run the Search

Run these commands from `UAVConfigFuzzer/` after building the library. 

Estimate the default configuration's setpoint sequence and scores:

```powershell
python -m uavfuzz estimate --out runs/baseline
```

Run 1-D search, then use its bounds for correlated n-D search:

```powershell
python -m uavfuzz 1d --out runs/search_1d --objective deviation --threshold 5 --n 20 --k 5 --iterations 10 --seed 42
python -m uavfuzz nd --single-bounds runs/search_1d/bounds.json --out runs/search_nd --objective deviation --threshold 5 --n 20 --k 5 --iterations 10 --seed 42
```


## Video Demo

We provide three videos showcasing three types of UAV anomalies caused by incorrect configurations.
* https://youtu.be/MfE_ELEV_GQ
* https://youtu.be/-i2bFYIB7O0
* https://youtu.be/4rUY63GKm9c

## License

This project is licensed under the [BSD 2-Clause License](LICENSE).
