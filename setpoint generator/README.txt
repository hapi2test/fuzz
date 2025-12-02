# Build Instructions
make px4_sitl_default

# How to Run
HEADLESS=1 make px4_sitl gazebo
setpoint_fuzzer <configuration parameter values> <flight missions>

## Example 
setpoint_fuzzer 5 10 45 3 4 8 4 -10 5 12 -3 3 3 1.5 1.5 1.5 0.7 12 45 47.3977 8.5455 488.0 47.3980 8.5460 488.0

## Example Output
Time,PosX,PosY,PosZ,VelX,VelY,VelZ,AccX,AccY,AccZ,TargetIdx
0,0,0,0,0,0,0,0,0,0,1
0.05,8.33333e-05,0,0,0.005,0,0,0.2,0,0,1
0.1,0.000666667,0,0,0.02,0,0,0.4,0,0,1