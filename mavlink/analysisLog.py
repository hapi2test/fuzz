import math

from pymavlink import mavutil
from pymavlink import mavwp
import time
import os
import sys
import logging
from pyulog import ULog
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd

def analyis_ulog(file_path):
    ulog = ULog(file_path)

    # 输出基本信息
    # print("Log start time:", ulog.start_timestamp)  # 日志开始时间（UNIX 时间戳）
    # print("Log duration:", ulog.last_timestamp - ulog.start_timestamp, "microseconds")  # 日志持续时间

    # 输出所有ourb
    # print("Available message names:")
    # for name in ulog.data_list:
    #     print(f"- {name.name}")

    # deviation
    score_deviation =  calculate_position_deviation_local(file_path)

    # rapid acent/decent
    msg_name = 'vehicle_local_position'
    score_rapi = if_rapid(ulog, msg_name)      # 加速度超过阈值的数量


    # interruption
    score_interruption = if_interrupt(ulog)   # 1 interruption

    # print(f"UAV status: deviation score {score_deviation}, rapid score {score_rapi}, interruption {score_interruption}")
    return score_deviation, score_rapi, score_interruption
    # print(score_deviation)
    # return score_deviation

def if_rapid(ulog,msg_name):
    new_list = {}
    error_list={}
    if msg_name in [msg.name for msg in ulog.data_list]:
        data = ulog.get_dataset(msg_name)

        for i in range(len(data.data['timestamp'])):
            new_list[i] = (data.data['timestamp'][i],data.data['az'][i])

    count = 0
    for i in range(len(new_list)):
        threshhold = 3
        if new_list[i][1] > threshhold:
            error_list[count] = (new_list[i][0],new_list[i][1])
            count += 1

    # print(len(error_list))
    return len(error_list)


def show_key(msg_name,ulog):
    if msg_name in [msg.name for msg in ulog.data_list]:
        data = ulog.get_dataset(msg_name)
        # 列出所有字段名
        fields = data.data.keys()
        print(f"Fields in '{msg_name}': {fields}")
    else:
        print(f"Message '{msg_name}' not found in the data list.")





def calculate_dis(new_list1,new_list2):
    data1 = np.array(new_list1)
    data2 = np.array(new_list2)

    timestamps1, x1_values, y1_values = data1[:, 0], data1[:, 1], data1[:, 2]
    timestamps2, x2_values, y2_values = data2[:, 0], data2[:, 1], data2[:, 2]

    results = []

    for t1, x1, y1 in zip(timestamps1, x1_values, y1_values):
        # 找到最接近的时间戳
        nearest_idx = np.argmin(np.abs(timestamps2 - t1))
        t2, x2, y2 = timestamps2[nearest_idx], x2_values[nearest_idx], y2_values[nearest_idx]

        # 检查时间戳差值是否超过 1000000
        if abs(t2 - t1) > 1000000:
            distance = 10
        else:
            # 计算欧几里得距离
            distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        # 保存到结果列表
        results.append((t1, t2, distance))


    error_list = []
    error_score = 0
    for i in range(len(results)):
        # print(results[i])
        if results[i][2] >1:
            error_list.append(results[i])
            error_score += results[i][2]
    # print("error result----------------------------")
    # print(len(error_list))
    # for i in range(len(error_list)):
    #     print(error_list[i])
    # print("error score:",error_score/len(new_list1))
    return error_score/len(new_list1)


# 1 卡死 时间窗口内 xyz的移动距离 是否超过阈值
def if_interrupt(ulog):

    # msg_name = 'estimator_local_position'
    msg_name = 'vehicle_global_position'
    new_list= []
    if msg_name in [msg.name for msg in ulog.data_list]:
        data = ulog.get_dataset(msg_name)
        for i in range(len(data.data['timestamp'])):
            new_list.append((data.data['timestamp'][i], data.data['lat'][i], data.data['lon'][i],data.data['alt'][i]))

    # for i in new_list:
    #     print(i)


    time_window = 10000000
    end_time = new_list[-1][0]
    start_time = end_time - time_window

    window_points = [point for point in new_list if point[0] >= start_time]
    # for point in window_points:
    #     print("window points:", point)

    # 判断最后一段时间的位移
    dx, dy, dz = 0,0,0
    if len(window_points) > 1:
        x_start, y_start, z_start = window_points[0][1], window_points[0][2], window_points[0][3]
        x_end, y_end, z_end = window_points[-1][1], window_points[-1][2], window_points[-1][3]

        # print("start:", x_start, y_start, z_start)
        # print("end:", x_end, y_end, z_end)

        # 计算总位移
        dx = x_end - x_start
        dy = y_end - y_start
        dz = z_end - z_start
        # print(abs(dx), abs(dy), abs(dz))

    if abs(dx)<0.5 and abs(dy)<0.5 and abs(dz)<0.5:
        # print("1")
        return 1
    else:
        return 0

def draw_figure(new_list,color):
    timestamps = [point[0] for point in new_list]
    x_coords = [point[1] for point in new_list]
    y_coords = [point[2] for point in new_list]

    # 绘制轨迹图
    plt.figure(figsize=(10, 8))
    plt.plot(x_coords, y_coords, marker='o', linestyle='-', color=color, alpha=0.7, label='Trajectory Path')

    # 添加标题和标签
    plt.title("Trajectory Setpoint Path (Relative Position)", fontsize=14)
    plt.xlabel("X (Relative Position)", fontsize=12)
    plt.ylabel("Y (Relative Position)", fontsize=12)
    plt.grid(True)
    plt.legend()
    plt.show()


def get_RQ2(ulog):
    print("Available message names:")
    for name in ulog.data_list:
        print(f"- {name.name}")

    # show_key('vehicle_global_position',ulog)

    msg_name = "vehicle_global_position"
    new_list = []
    if msg_name in [msg.name for msg in ulog.data_list]:
        data = ulog.get_dataset(msg_name)
        for i in range(len(data.data['timestamp'])):
            new_list.append((data.data['timestamp'][i], data.data['lat'][i], data.data['lon'][i],data.data['alt'][i]))

    msg_name2 = 'position_setpoint_triplet'
    new_list2 = []
    if msg_name2 in [msg.name for msg in ulog.data_list]:
        data = ulog.get_dataset(msg_name2)
        for i in range(len(data.data['current.timestamp'])):
            if not math.isnan(data.data['current.lat'][i]):
                new_list2.append((data.data['current.timestamp'][i], data.data['current.lat'][i], data.data['current.lon'][i],data.data['current.alt'][i]))

    for item in new_list:
        print(item)

    print("---------------------")

    for item in new_list2:
        print(item)


    data1 = np.array(new_list)
    data2 = np.array(new_list2)

    timestamps1, x1_values, y1_values = data1[:, 0], data1[:, 1], data1[:, 2]
    timestamps2, x2_values, y2_values = data2[:, 0], data2[:, 1], data2[:, 2]

    results = []
    for t1, x1, y1 in zip(timestamps1, x1_values, y1_values):
        # 找到最接近的时间戳
        nearest_idx = np.argmin(np.abs(timestamps2 - t1))
        t2, x2, y2 = timestamps2[nearest_idx], x2_values[nearest_idx], y2_values[nearest_idx]

        # 检查时间戳差值是否超过 1000000
        if abs(t2 - t1) > 1000000:
            lat_dis = 1
            lon_dis = 1
        else:
            # 计算欧几里得距离
            lat_dis = abs(x2 - x1)
            lon_dis = abs(y2 - y1)

        # 保存到结果列表
        results.append((t1, t2, lat_dis,lon_dis))

    for item in results:
        if item[2] !=1:
            print(item)

def RQ2(ulog):
    # print("Available message names:")
    # for name in ulog.data_list:
    #     print(f"- {name.name}")

    show_key('vehicle_global_position',ulog)

    msg_name = "vehicle_global_position"
    new_list = []
    if msg_name in [msg.name for msg in ulog.data_list]:
        data = ulog.get_dataset(msg_name)
        for i in range(len(data.data['timestamp'])):
            new_list.append((data.data['timestamp'][i], data.data['lat'][i], data.data['lon'][i], data.data['alt'][i]))

    msg_name2 = 'position_setpoint_triplet'
    new_list2 = []
    if msg_name2 in [msg.name for msg in ulog.data_list]:
        data = ulog.get_dataset(msg_name2)
        for i in range(len(data.data['current.timestamp'])):
            if not math.isnan(data.data['current.lat'][i]):
                new_list2.append((data.data['current.timestamp'][i], data.data['current.lat'][i],
                                  data.data['current.lon'][i], data.data['current.alt'][i]))

    # for item in new_list:
    #     print(item)

    # print("---------------------")
    #
    # for item in new_list2:
    #     print(item)
    #
    # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
    #
    data1 = np.array(new_list)
    data2 = np.array(new_list2)

    timestamps1, x1_values, y1_values, z1_values= data1[:, 0], data1[:, 1], data1[:, 2],data1[:, 3]
    timestamps2, x2_values, y2_values, z2_value = data2[:, 0], data2[:, 1], data2[:, 2],data2[:, 3]

    results = []
    for t1, x1, y1, z1 in zip(timestamps1, x1_values, y1_values,z1_values):
        # 找到最接近的时间戳
        nearest_idx = np.argmin(np.abs(timestamps2 - t1))
        t2, x2, y2, z2 = timestamps2[nearest_idx], x2_values[nearest_idx], y2_values[nearest_idx], z2_value[nearest_idx]

        # 检查时间戳差值是否超过 1000000
        if abs(t2 - t1) > 5000000:
            lat_dis = 1
            lon_dis = 1
            alt_dis = 1
        else:
            lat_dis = abs(x1-x2)
            lon_dis = abs(y1-y2)
            alt_dis = abs(z1-z2)

        # 保存到结果列表
        results.append((t1, t2, lat_dis,lon_dis,alt_dis))

    seen_t2 = set()
    unique_results = []

    for result in results:
        t1, t2, lat_dis, lon_dis, alt_dis = result
        if t2 not in seen_t2:
            unique_results.append(result)
            seen_t2.add(t2)

    # 输出去重后的结果

    for item in unique_results:
        if item[2] !=1:
            print(item)


def get_time(ulog):
    msg_name = "vehicle_global_position"
    new_list = []
    if msg_name in [msg.name for msg in ulog.data_list]:
        data = ulog.get_dataset(msg_name)
        for i in range(len(data.data['timestamp'])):
            new_list.append((data.data['timestamp'][i], data.data['lat'][i], data.data['lon'][i], data.data['alt'][i]))

    msg_name2 = 'position_setpoint_triplet'
    new_list2 = []
    if msg_name2 in [msg.name for msg in ulog.data_list]:
        data = ulog.get_dataset(msg_name2)
        for i in range(len(data.data['current.timestamp'])):
            if not math.isnan(data.data['current.lat'][i]):
                new_list2.append((data.data['current.timestamp'][i], data.data['current.lat'][i],
                                  data.data['current.lon'][i], data.data['current.alt'][i]))
    # 找到与 new_list2 中每个坐标最接近的 new_list 项，并计算时间戳差距
    results = []
    for timestamp2, lat2, lon2, alt2 in new_list2:
        min_diff = float('inf')
        closest_item = None
        for timestamp1, lat1, lon1, alt1 in new_list:
            # 计算 lat 和 lon 差值的和
            diff = abs(lat2 - lat1) + abs(lon2 - lon1)
            if diff < min_diff:
                min_diff = diff
                closest_item = (timestamp1, lat1, lon1, alt1)

        if closest_item:
            time_diff = abs(timestamp2 - closest_item[0])  # 时间戳差异
            results.append((timestamp2, lat2, lon2, alt2, closest_item[0], min_diff, time_diff))

    # 输出结果
    for result in results:
        # print(f"Target: (timestamp={result[0]}, lat={result[1]}, lon={result[2]}, alt={result[3]})")
        # print(f"Closest: (timestamp={result[4]}, diff_sum={result[5]:.8f}, time_diff={result[6]} microseconds)")
        print(result[5])


def load_local_position_data(file_path, msg_name="vehicle_local_position", downsample_factor=10):
    ulog = ULog(file_path)
    new_list = []
    if msg_name in [msg.name for msg in ulog.data_list]:
        data = ulog.get_dataset(msg_name)
        for i in range(len(data.data['timestamp'])):
            new_list.append((data.data['timestamp'][i], data.data['x'][i], data.data['y'][i]))
    return downsample_positions(new_list, downsample_factor)

def downsample_positions(positions, factor=10):
    return positions[::factor]

def find_nearest_point(ref_points, test_point):
    distances = [np.linalg.norm((ref[1] - test_point[1], ref[2] - test_point[2])) for ref in ref_points]
    min_index = np.argmin(distances)
    return min_index, distances[min_index]


def calculate_position_deviation_local(test_file):
    reference_file = './normal.ulg'
    reference_positions = load_local_position_data(reference_file)
    test_positions = load_local_position_data(test_file)

    print("------------")
    print(len(reference_positions),len(test_positions))
    deviations = []
    for test_point in test_positions:
        _, deviation = find_nearest_point(reference_positions, test_point)
        deviations.append(deviation)

    max_deviation = max(deviations)

    return max_deviation

def quick_get_log_test():
    log_dir = "/home/gazebo/Desktop/PX4-Autopilot/build/px4_sitl_default/rootfs/log/2024-12-12/"

    log_files = sorted(
        os.listdir(log_dir),
        key=lambda x: os.path.getmtime(os.path.join(log_dir, x)),
        reverse=True
    )
    log_name = log_files[0]
    print(f"Log Name: {log_name}")

    cmd = (
        'cd /home/gazebo/Desktop/PX4-Autopilot/build/px4_sitl_default/rootfs/log/2024-12-12/ &&'
        'cp "$(ls -t | head -n1)" ~/Desktop/px4Test/'
    )
    os.system(cmd)
    log_path = "/home/gazebo/Desktop/px4Test/" + log_name

    score1, score2, score3 = analyis_ulog(log_path)
    print(score1,score2,score3)


if __name__=='__main__':
    # log_path = './09_08_08.ulg'
    # score1,score2,score3 = analyis_ulog(log_path)
    # print(score1,score2,score3)
    # file_path = 'devi.ulg'
    # score1, score2,score3 = analyis_ulog(file_path)
    # print(score1,score2,score3)
    quick_get_log_test()


