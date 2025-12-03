# UAVConfigFuzzer Code Repository

This repository contains the code for the **UAVConfigFuzzer** project. Below is an overview of the directory structure and functionality:

## Directory Structure

- **DLL**: Contains the code for setpoint estimator based on static analysis.
- **mutation**：One-dimensional and multi-dimensional mutation based on **setpoint generator**.
- **GAradom**: Contains the code for **UAVConfigFuzzer**, which includes the following features:
  - Binary search method mutation.
  - Genetic algorithms mutation.
- **mavlnk**: Contains code based on the **MAVLink** protocol for injecting configuration parameters into simulator and checking the status of UAV.
- **setpoint generator**: Contains the code for **setpoint generator**.

## Video Demo

We provide three videos showcasing three types of UAV anomalies caused by incorrect configurations.
* https://youtu.be/MfE_ELEV_GQ
* https://youtu.be/-i2bFYIB7O0
* https://youtu.be/4rUY63GKm9c

## License

This project is licensed under the BSD 2-Clause License.



