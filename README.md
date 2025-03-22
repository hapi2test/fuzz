# ParamFuzzer Code Repository

This repository contains the code for the **ParamFuzzer** project. Below is an overview of the directory structure and functionality:

## Directory Structure

- **DLL**: Contains the code for **Param2SP**.
- **GAradom**: Contains the code for **ParamFuzzer**, which includes the following features:
  - One-dimensional and multi-dimensional mutation based on **Param2SP**.
  - Binary search method mutation.
  - Genetic algorithms mutation.
- **mavlnk**: Contains code based on the **MAVLink** protocol for injecting configuration parameters into simulator and checking the status of UAV.
- **Data**: Contains partial results generated by ParamFuzzer.

## Project Overview

**ParamFuzzer** is a fuzzing tool that leverages setpoint generation code as enhanced feedback to optimize the process.

## video demo
We provide three videos showcasing three types of UAV anomalies caused by incorrect configurations.
* https://youtu.be/MfE_ELEV_GQ
* https://youtu.be/-i2bFYIB7O0
* https://youtu.be/4rUY63GKm9c

## License

This project is licensed under the BSD 2-Clause License.
