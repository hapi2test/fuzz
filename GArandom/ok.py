import re

'''
from geopy.distance import geodesic


def calculate_distance(coord1, coord2):

    distance = geodesic(coord1, coord2).meters
    return distance

# 示例输入
coord1 = (47.39746562, 8.545591383)  # 北京天安门
coord2 = (47.39746559, 8.545590282)  # 上海外滩

# 计算并输出距离
distance = calculate_distance(coord1, coord2)
print(f"两个坐标之间的距离是 {distance:.2f} 米")

'''

lines_data = """
[*] Position Hint - X: 0.898624, Y: 0.247825, Z: 0)
[*] Home Position - X: 0.898624, Y: 0.247825, Z: 25.25
[*] Check: takeoff: NAV_ACC_RAD >= 0 : 1
[*] Estimated take off time: 18.0581
[*] Yaw alignment time: 0.23067
[*] Estimated time cost: 15.1746
[*] Last Position - X: 0.898344, Y: 0.247145, Z: 27.39
[*] Yaw alignment time: 0.0606552
[*] Estimated time cost: 13.8171
[*] Last Position - X: 0.898254, Y: 0.247815, Z: 29.95
[*] Yaw alignment time: 0.652016
[*] Estimated time cost: 12.4258
[*] Last Position - X: 0.898574, Y: 0.247335, Z: 31.33
[*] Yaw alignment time: 1.287
[*] Estimated time cost: 22.8444
"""

# 使用正则表达式查找所有X和Y坐标
coordinates = re.findall(r"X:\s*([-\d.]+),\s*Y:\s*([-\d.]+)", lines_data)


print(coordinates)
# 输出提取结果
for idx, (x, y) in enumerate(coordinates, start=1):
    print(f"Position {idx}: X = {x}, Y = {y}")
