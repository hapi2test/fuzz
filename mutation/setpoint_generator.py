# 自动化执行 px4的setpoint generator
# 输入 配置参数，飞行计划
# 输出 setpoints sequence

import subprocess
import datetime
import os

config_params = [
    5, 10, 45, 3, 4, 8, 4, -10, 5,
    12, -3, 3, 3, 1.5, 1.5, 1.5, 0.7, 12, 45
]

flight_plan = [

]

def run_setpoint_generator(config_params,flight_plan):
    EXECUTABLE = "./setpoint_fuzzer"


    OUTPUT_DIR = "logs"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile = os.path.join(OUTPUT_DIR, f"logs.txt")


    cmd = [EXECUTABLE] + [str(x) for x in config_params] + [str(x) for x in flight_plan]

    with open(outfile, "w") as f:
        process = subprocess.Popen(
            cmd,
            stdout=f,
            stderr=f,
            text=True
        )
        process.wait()

