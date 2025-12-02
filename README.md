# UAVConfigFuzzer Code Repository

This repository contains the code for the **UAVConfigFuzzer** project. Below is an overview of the directory structure and functionality:

## Directory Structure

- **DLL**: Contains the code for setpoint estimator based on static analysis.
- **GAradom**: Contains the code for **UAVConfigFuzzer**, which includes the following features:
  - One-dimensional and multi-dimensional mutation based on **setpoint generator**.
  - Binary search method mutation.
  - Genetic algorithms mutation.
- **mavlnk**: Contains code based on the **MAVLink** protocol for injecting configuration parameters into simulator and checking the status of UAV.
- **setpoint generator**: Contains the code for **setpoint generator**.

## Project Overview

**UAVConfigFuzzer** is a fuzzing tool that bypasses the bottleneck of time-consuming simulations by utilizing a headless setpoint generator to rapidly estimate UAV physical states.

## How to Use 

- The Param2SP is wrapped as a dll, "myDllposition.dll".
  - You can directly call this dll using python ``myDll = ctypes.cdll.LoadLibrary('./myDllposition.dll')``, and its input is a flight plan, like **AVC2013_mission**
  - ``QGC WPL 110
      0	1	0	16	0.000000	0.000000	0.000000	0.000000	40.072842	-105.230575	0.000000	1
      1	0	3	22	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	10.000000	1
      2	0	3	16	5.000000	0.000000	0.000000	0.000000	40.075676	-105.232285	20.000000	1
      3	0	3	203	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	1
      4	0	3	16	1.000000	0.000000	0.000000	0.000000	40.072514	-105.231544	20.000000	1
      5	0	3	16	0.000000	0.000000	0.000000	0.000000	40.072514	-105.231544	3.000000	1
      6	0	3	178	1.000000	5.000000	0.000000	0.000000	0.000000	0.000000	0.000000	1
      7	0	3	16	0.000000	0.000000	0.000000	0.000000	40.072544	-105.231354	3.000000	1
      8	0	3	16	0.000000	0.000000	0.000000	0.000000	40.072609	-105.231285	5.000000	1
      9	0	3	21	0.000000	0.000000	0.000000	0.000000	40.072845	-105.230576	0.000000	1``
  - You can find the example flight mission data structure in ``mission.py`` and change the mission to yours.
- You can test the fuzzing process just run the ``main.py``
  - the project contains the unit tests about different functions, you can test different the fuzzing strategies.
- ENV
  - python 3.11  

## Video Demo

We provide three videos showcasing three types of UAV anomalies caused by incorrect configurations.
* https://youtu.be/MfE_ELEV_GQ
* https://youtu.be/-i2bFYIB7O0
* https://youtu.be/4rUY63GKm9c

## License

This project is licensed under the BSD 2-Clause License.


