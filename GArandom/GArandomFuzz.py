import config
import mission
import ctypes
import math
import os
import random
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import time
import config
import re


'''
lines data
三个种类要不要区分?
'''
def getWarning(lines_data):
    warnings = []
    for line in lines_data:
        if '[!]' in line:
            warnings.append(line)
    return warnings
def calculate_distance(point1,point2):
    x1,y1,z1 = point1
    x2,y2,z2 = point2
    R = 6371000
    x1_earth = (R + z1) * math.cos(x1) * math.cos(y1)
    y1_earth = (R + z1) * math.cos(x1) * math.sin(y1)
    z1_earth =  (R + z1) * math.sin(x1)

    x2_earth = (R + z2) * math.cos(x2) * math.cos(y2)
    y2_earth = (R + z2) * math.cos(x2) * math.sin(y2)
    z2_earth = (R + z2) * math.sin(x2)

    dis = math.sqrt((x1_earth-x2_earth)**2 + (y1_earth-y2_earth)**2 + (z1_earth-z2_earth)**2)
    return dis
def getpoints(commands):
    xyz_coords = []
    for command in commands:
        xyz = (command[8],command[9],command[10])
        xyz_coords.append(xyz)
    distance =[]
    for i in range(len(xyz_coords) - 2):
        dis = calculate_distance(xyz_coords[i],xyz_coords[i+1])
        distance.append(dis)

    return distance

def extractTime(lines_data):
    time_data=[]
    for line in lines_data:
        if 'Estimated' in line and 'time' in line:
            time_data.append(line)

    times = []
    for i in time_data:
        split_result = i.split()
        number = split_result[-1]
        if number=='inf' or number =='-nan(ind)':
            num = 999
        else:
            num = float(number)
        times.append(num)

    return times
def calculate_velocity(distance,time):
    velocity =[]
    for i in range(len(time)):
        if time[i] ==0:
            velocity.append(999)
        else:
            v = distance[i] / time[i]
            velocity.append(v)

    return velocity

def calculate_acc(valocity,time):
    acc = []
    for i in range(len(time)-1):
        a = (valocity[i+1] - valocity[i]) /time[i]
        acc.append(a)
    return acc

def rapid(commands,lines_data):

    score = 0
    distance = getpoints(commands)
    time = extractTime(lines_data)
    velocity = calculate_velocity(distance, time)
    time.pop()
    velocity.pop()
    acc = calculate_acc(velocity,time)
    # print(max(acc))
    return max(acc)


def deviation(individual,warnings):

    configParam= list(individual.values())

    cannotWarnings = []
    for warning in warnings:
        if 'failed' in warning or 'cannot' in warning:
            cannotWarnings.append(warning)
    cannotWarningsLen = len(cannotWarnings)

    if cannotWarningsLen != 0:
        score = cannotWarningsLen
    else:
        # Yaw alignment time is beyond MIS_YAW_TMT
        # MPC_YAWRAUTO_MAX 15 MIS_YAW_TMT 2 ERR 12
        temp1 = abs(configParam[12] / (configParam[15] +1e-10) - configParam[2])

        # Climb rate is too slow!
        # MPC_XY_CRUISE 17 MPC_ACC_UP_MAX 20 MPC_Z_V_AUTO_UP 21
        temp2 = abs((configParam[20] + configParam[21]) - configParam[17])

        # Descend rate is too slow
        # MPC_ACC_DOWN_MAX 18 + MPC_Z_V_AUTO_DN 19 - MPC_XY_CRUISE 17
        temp3 = abs((configParam[18] + configParam[19]) - configParam[17])

        # Pitch rate is too slow! T
        # NAV_ACC_RAD 14 / MC_PITCHRATE_MAX 6 - MPC_Z_V_AUTO_UP 21
        temp4 = abs(configParam[14] / (configParam[6]+1e-10) - configParam[21])

        # Yaw rate is too slow!
        # MIS_YAW_ERR 12 / MPC_YAWRAUTO_MAX 15 - MPC_Z_V_AUTO_UP 21
        temp5 = abs(configParam[12] / (configParam[15]+1e-10) - configParam[21])

        temp_value = [temp1, temp2, temp3, temp4, temp5]
        min_temp_value = min(temp_value)
        score = min_temp_value / (temp1 + temp2 + temp3 + temp4 + temp5)

    return score

def get_waypoints(mission):
    waypoints = []
    for i in range(len(mission)):
        x = mission[i][8]
        y = mission[i][9]
        waypoints.append([x,y])
    return waypoints
def get_output_points(lines_data):

    waypoints = []
    for lines in lines_data:
        coordinates = re.findall(r"X:\s*([-\d.]+),\s*Y:\s*([-\d.]+)", lines)
        if coordinates != []:
            waypoints.append(coordinates)
    return waypoints


def min_distance_setpoints(waypoints, setpoints):
    min_distances = []

    for setpoint in setpoints:

        dis = []
        for i in range(len(waypoints) - 1):
            A = waypoints[i]
            B = waypoints[i + 1]
            distance = point_to_segment_distance(A, B, setpoint)
            dis.append(distance)
        # print(setpoint,i,dis)
        min_distances.append(min(dis))
    # print(min_distances)
    return min_distances


def point_to_segment_distance(A, B, C):
    x_A, y_A = A
    x_B, y_B = B
    x_C, y_C = C

    AB = (x_B - x_A, y_B - y_A)
    AC = (x_C - x_A, y_C - y_A)
    AB_length_squared = AB[0] ** 2 + AB[1] ** 2

    if AB_length_squared == 0:
        return math.sqrt(AC[0] ** 2 + AC[1] ** 2)  # 返回 A 到 C 的距离

    # 计算投影比例 t
    t = (AC[0] * AB[0] + AC[1] * AB[1]) / AB_length_squared
    t = max(0, min(1, t))
    D = (x_A + t * AB[0], y_A + t * AB[1])

    distance = math.sqrt((x_C - D[0]) ** 2 + (y_C - D[1]) ** 2)

    return distance

def Deviation_line(mission,lines_data):
    waypoints = get_waypoints(mission)
    # 返回len -1条直线
    output_points = get_output_points(lines_data)
    # 点到所有直线的距离
    # 取最小值
    temp = min_distance_setpoints(waypoints, output_points)

    return max(temp)

def testDeviation():
    waypoints = [
        [0,0],
        [2,2],
        [3,2],
        [4,0]
    ]
    setpoints = [
        [0, 0],
        [1,1],
        [2, 2],
        [2.5,2.5],
        [3, 2],
        [3.5,2],
        [4, 0]
    ]
    temp = min_distance_setpoints(waypoints, setpoints)
    print(temp)
    print(max(temp))

def interruption(individual,warnings):
    configParam = list(individual.values())

    warningDevide = []
    for warning in warnings:
        if 'Devided by zero' in warning:
            warningDevide.append(warning)

    warningDevideLen = len(warningDevide)
    if warningDevideLen != 0:
        score = warningDevideLen * 5
    else:
        abs_diff_A = abs(configParam[17])
        abs_diff_B = abs(configParam[19])
        abs_diff_C = abs(configParam[21])
        abs_diff_D = abs(configParam[23])

        temp = [abs_diff_A, abs_diff_B, abs_diff_C, abs_diff_D]
        minTemp = min(temp)
        score = minTemp / (abs_diff_A + abs_diff_B + abs_diff_C + abs_diff_D +1e-10)
        score = score *5

    return score
def calculate_fitness(configurations,lines_data,commands,flag):

    warnings = getWarning(lines_data)

    # flag = 2
    if flag ==0:
        score  = rapid(commands,lines_data)
    elif flag ==1:
        score = deviation(configurations,warnings)
    elif flag ==2:
        score = interruption(configurations,warnings)

    return score

def getDll(configurations,missionNum, mission,flag):
    useDll(configurations, missionNum, mission)
    lines_data = readOutputFIle()
    warnings = getWarning(lines_data)
    score = calculate_fitness(configurations, lines_data, mission,flag)

    if len(warnings)!=0:
        return 999
    else:
        return score

'''
dll 返回的信息
'''
def useDll(individual,commandNum,commands):
    # 加载 C++ DLL
    myDll = ctypes.cdll.LoadLibrary('./myDllposition.dll')

    newValues= list(individual.values())

    newValuesSize = len(newValues)

    commandsCount = len(commands)

    newValues_arr = (ctypes.c_double * newValuesSize)(*newValues)

    commands_pointers = (ctypes.POINTER(ctypes.c_double) * commandsCount)()
    sizes_arr = (ctypes.c_size_t * commandsCount)()

    for i, cmd in enumerate(commands):
        sizes_arr[i] = len(cmd)
        commands_pointers[i] = (ctypes.c_double * len(cmd))(*cmd)

    myDll.init(newValues_arr, newValuesSize, commandNum, commands_pointers, sizes_arr, commandsCount)

def readOutputFIle():
    file_path = 'output.txt'
    lines_data = []

    with open(file_path, 'r') as file:
        for line in file:
            lines_data.append(line.strip())

    return lines_data


def warning_count(config,missionNum,mission):
    useDll(config, missionNum, mission)
    lines_data = readOutputFIle()
    warnings =getWarning(lines_data)

    # print(warnings)

    return len(warnings)
    # print("test---------------------")
    # print(len(warnings))

test ={'MPC_TKO_RAMP_T': 3, 'MIS_DIST_1WP': 900, 'MIS_YAW_TMT': -1, 'MPC_LAND_ALT1': 10, 'MIS_DIST_WPS': 900, 'MPC_Z_VEL_MAX_UP': 3, 'MC_PITCHRATE_MAX': 220, 'NAV_MC_ALT_RAD': 0.8, 'MIS_TAKEOFF_ALT': 2.5, 'MPC_LAND_ALT3': 1, 'NAV_FW_ALTL_RAD': 5, 'MPC_XY_VEL_MAX': 12, 'MIS_YAW_ERR': 12, 'NAV_FW_ALT_RAD': 10, 'NAV_ACC_RAD': 5, 'MPC_YAWRAUTO_MAX': 45, 'MPC_THR_MAX': 1, 'MPC_XY_CRUISE': 5, 'MPC_ACC_DOWN_MAX': 3, 'MPC_Z_V_AUTO_DN': 1.5, 'MPC_ACC_UP_MAX': 4, 'MPC_Z_V_AUTO_UP': 3, 'MPC_Z_VEL_MAX_DN': 1.5, 'MPC_TKO_SPEED': 1.5, 'MPC_TILTMAX_AIR': 45, 'MPC_JERK_AUTO': 4, 'MPC_ACC_HOR': 3, 'MPC_LAND_SPEED': 0.7, 'MPC_LAND_ALT2': 5, 'MPC_LAND_CRWL': 0.3, 'MPC_YAW_MODE': 4, 'MC_YAWRATE_MAX': 200, 'MC_YAW_WEIGHT': 0.4, 'MPC_Z_VEL_ALL': -3, 'SYS_VEHICLE_RESP': 0.3, 'MPC_ACC_HOR_MAX': 5, 'MPC_JERK_MAX': 8, 'MPC_XY_VEL_ALL': 0, 'MPC_TILTMAX_LND': 12, 'MPC_THR_HOVER': 0.5, 'MPC_THR_MIN': 0.2}


if __name__ == '__main__':

    # useDll(config.configuration_default,mission.commandNum21,mission.commands21)
    # score = getDll(config.configuration,mission.commandNum21,mission.commands21,0)
    # score = getDll(config.configuration,mission.commandNum21,mission.commands21,2)
    #
    # print("fitness")
    # print(score)

    # warning_count(test,mission.commandNum21,mission.commands21)



    #
    # useDll(config.configuration, mission.commandNum21, mission.commands21)
    # lines_data = readOutputFIle()
    # Deviation_line(mission.commands21,lines_data)

    testDeviation()