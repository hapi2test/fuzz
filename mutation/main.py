# 变异的主函数
# 输入 飞行计划
# 默认配置列表变异算法 -》配置参数
# setpoint generator
# setpoint sequence -》test Oracle fitness scores


import os
import math
import random
import numpy as np
import setpoint_generator


DEFAULT_CONFIG = [
    5, 10, 45, 3, 4, 8, 4, -10, 5,
    12, -3, 3, 3, 1.5, 1.5, 1.5, 0.7, 12, 45
]

PLANS = [
]

INITIAL_BOUNDS = [
    (0, 15), (2, 15), (20, 89), (0.8, 15), (1, 15),
    (2, 50), (1, 25), (-20, 999), (-1, 50),
    (0, 999), (-3, 999), (-1, 10), (-1, 10),
    (-1, 10), (-1, 999), (0, 999), (0, 999),
    (0, 999), (-1, 999)
]



def get_setpoint(config,mission):
    setpoint_generator.run_setpoint_generator(config, mission)
    txt_files = [f for f in os.listdir(".") if f.endswith(".txt")]
    latest = max(txt_files, key=os.path.getmtime)
    return latest



def load_setpoints(txt_file):
    time_list = []
    pos = []
    vel = []
    acc = []

    with open(txt_file, "r") as f:
        next(f)
        for line in f:
            parts = line.strip().split(",")

            t = float(parts[0])
            px, py, pz = map(float, parts[1:4])
            vx, vy, vz = map(float, parts[4:7])
            ax, ay, az = map(float, parts[7:10])

            time_list.append(t)
            pos.append([px, py, pz])
            vel.append([vx, vy, vz])
            acc.append([ax, ay, az])

    return np.array(time_list), np.array(pos), np.array(vel), np.array(acc)



def test_get_setpoints(config,mission):
    txt_path = "./logs.txt"
    return txt_path

def fitness_rapid_ascent_descent(acc):
    return np.max(np.abs(acc[:, 2]))

def gps_to_ned(lat, lon, alt, lat0, lon0, alt0):
    R_EARTH = 6378137.0
    d_lat = math.radians(lat - lat0)
    d_lon = math.radians(lon - lon0)
    north = d_lat * R_EARTH
    east  = d_lon * R_EARTH * math.cos(math.radians(lat0))
    down  = -(alt - alt0)
    return np.array([north, east, down])

def convert_waypoints_to_ned(waypoints):
    lat0, lon0, alt0 = waypoints[0]   # 原点参考点
    ned_points = []
    for lat, lon, alt in waypoints:
        ned = gps_to_ned(lat, lon, alt, lat0, lon0, alt0)
        ned_points.append(ned)
    return ned_points


def line_segment_distance(point, a, b):
    ap = point - a
    ab = b - a
    t = np.dot(ap, ab) / np.dot(ab, ab)
    t = max(0, min(1, t))
    proj = a + t * ab
    return np.linalg.norm(point - proj)

def reshape_flat_gps_list(flat_list):
    if len(flat_list) % 3 != 0:
        raise ValueError("PLANS must contains（lat, lon, alt）")

    waypoints = []
    for i in range(0, len(flat_list), 3):
        lat = float(flat_list[i])
        lon = float(flat_list[i+1])
        alt = float(flat_list[i+2])
        waypoints.append((lat, lon, alt))
    return waypoints


def fitness_deviation(pos, waypoints_gps):
    waypoints_gps = reshape_flat_gps_list(waypoints_gps)

    waypoints = convert_waypoints_to_ned(waypoints_gps)

    max_dev = 0
    for i in range(len(waypoints) - 1):
        a = np.array(waypoints[i])
        b = np.array(waypoints[i + 1])
        for p in pos:
            d = line_segment_distance(p, a, b)
            max_dev = max(max_dev, d)

    return max_dev



def fitness_interruption(vel, complete=True):
    if not complete:
        return float("inf")

    speed = np.linalg.norm(vel, axis=1)
    min_speed = np.min(speed)
    return 1.0 / (min_speed + 1e-6)


def compute_fitness(setpoint_file, waypoints, is_complete=True):
    t, pos, vel, acc = load_setpoints(setpoint_file)

    return {
        "rapid": fitness_rapid_ascent_descent(acc),
        "deviation": fitness_deviation(pos, waypoints),
        "interruption": fitness_interruption(vel, is_complete)
    }


def mutate_1d_for_rapid(param_index, N=20, K=5, iterations=10):
    low, high = INITIAL_BOUNDS[param_index]
    candidates = []
    candidate_scores = []

    for _ in range(iterations):
        configs = []

        for _ in range(N):
            c = DEFAULT_CONFIG.copy()
            c[param_index] = round(random.uniform(low, high) / 0.5) * 0.5
            configs.append(c)

        scored = []
        for c in configs:
            out = get_setpoint(c, PLANS)
            fv = compute_fitness(out, PLANS)
            rapid_score = fv["rapid"]
            scored.append((rapid_score, c))

        scored.sort(reverse=True, key=lambda x: x[0])
        seeds = scored[:K]

        seed_values = [c[param_index] for _, c in seeds]
        new_low = min(seed_values)
        new_high = max(seed_values)
        span = new_high - new_low
        low = new_low - 0.5 * span
        high = new_high + 0.5 * span

        for s, c in seeds:
            candidates.append(c)
            candidate_scores.append(s)

    return candidates, candidate_scores




def mutate_1d_for_deviation(param_index, N=20, K=5, iterations=10):
    low, high = INITIAL_BOUNDS[param_index]
    candidates = []
    candidate_scores = []

    for _ in range(iterations):
        configs = []

        for _ in range(N):
            c = DEFAULT_CONFIG.copy()
            c[param_index] = round(random.uniform(low, high) / 0.5) * 0.5
            configs.append(c)

        scored = []
        for c in configs:
            out = get_setpoint(c, PLANS)
            fv = compute_fitness(out, PLANS)
            rapid_score = fv["deviation"]
            scored.append((rapid_score, c))

        scored.sort(reverse=True, key=lambda x: x[0])
        seeds = scored[:K]

        seed_values = [c[param_index] for _, c in seeds]
        new_low = min(seed_values)
        new_high = max(seed_values)
        span = new_high - new_low
        low = new_low - 0.5 * span
        high = new_high + 0.5 * span

        for s, c in seeds:
            candidates.append(c)
            candidate_scores.append(s)

    return candidates, candidate_scores

def mutate_1d_for_interruption(param_index, N=20, K=5, iterations=10):
    low, high = INITIAL_BOUNDS[param_index]
    candidates = []
    candidate_scores = []

    for _ in range(iterations):
        configs = []

        for _ in range(N):
            c = DEFAULT_CONFIG.copy()
            c[param_index] = round(random.uniform(low, high) / 0.5) * 0.5
            configs.append(c)

        scored = []
        for c in configs:
            out = get_setpoint(c, PLANS)
            fv = compute_fitness(out, PLANS)
            rapid_score = fv["interruption"]
            scored.append((rapid_score, c))

        scored.sort(reverse=True, key=lambda x: x[0])
        seeds = scored[:K]

        seed_values = [c[param_index] for _, c in seeds]
        new_low = min(seed_values)
        new_high = max(seed_values)
        span = new_high - new_low
        low = new_low - 0.5 * span
        high = new_high + 0.5 * span

        for s, c in seeds:
            candidates.append(c)
            candidate_scores.append(s)

    return candidates, candidate_scores


def mutate_nd_for_rapid(target_idx, correlated_idx, N=20, K=5, iterations=10):
    low, high = INITIAL_BOUNDS[target_idx]
    candidates = []
    candidate_scores = []

    for _ in range(iterations):
        configs = []

        for _ in range(N):
            c = DEFAULT_CONFIG.copy()
            c[target_idx] = round(random.uniform(low, high) / 0.5) * 0.5

            c[correlated_idx] = random.choice([INITIAL_BOUNDS[correlated_idx][0], INITIAL_BOUNDS[correlated_idx][1], DEFAULT_CONFIG[correlated_idx]])

            configs.append(c)
        print("test", configs)
        scored = []
        for c in configs:
            out = get_setpoint(c, PLANS)
            fv = compute_fitness(out, PLANS)
            rapid_score = fv["rapid"]
            scored.append((rapid_score, c))

        scored.sort(reverse=True, key=lambda x: x[0])
        seeds = scored[:K]

        seed_values = [c[target_idx] for _, c in seeds]
        new_low = min(seed_values)
        new_high = max(seed_values)
        span = new_high - new_low
        low = new_low - 0.5 * span
        high = new_high + 0.5 * span

        for s, c in seeds:
            candidates.append(c)
            candidate_scores.append(s)

    return candidates, candidate_scores

def mutate_nd_for_deviation(target_idx, correlated_idx, N=20, K=5, iterations=10):
    low, high = INITIAL_BOUNDS[target_idx]
    candidates = []
    candidate_scores = []

    for _ in range(iterations):
        configs = []

        for _ in range(N):
            c = DEFAULT_CONFIG.copy()
            c[target_idx] = round(random.uniform(low, high) / 0.5) * 0.5

            c[correlated_idx] = random.choice([INITIAL_BOUNDS[correlated_idx][0], INITIAL_BOUNDS[correlated_idx][1], DEFAULT_CONFIG[correlated_idx]])

            configs.append(c)
        # print("test", configs)
        scored = []
        for c in configs:
            out = get_setpoint(c, PLANS)
            fv = compute_fitness(out, PLANS)
            rapid_score = fv["deviation"]
            scored.append((rapid_score, c))

        scored.sort(reverse=True, key=lambda x: x[0])
        seeds = scored[:K]

        seed_values = [c[target_idx] for _, c in seeds]
        new_low = min(seed_values)
        new_high = max(seed_values)
        span = new_high - new_low
        low = new_low - 0.5 * span
        high = new_high + 0.5 * span

        for s, c in seeds:
            candidates.append(c)
            candidate_scores.append(s)

    return candidates, candidate_scores

def mutate_nd_for_interruption(target_idx, correlated_idx, N=20, K=5, iterations=10):
    low, high = INITIAL_BOUNDS[target_idx]
    candidates = []
    candidate_scores = []

    for _ in range(iterations):
        configs = []

        for _ in range(N):
            c = DEFAULT_CONFIG.copy()
            c[target_idx] = round(random.uniform(low, high) / 0.5) * 0.5

            c[correlated_idx] = random.choice([INITIAL_BOUNDS[correlated_idx][0], INITIAL_BOUNDS[correlated_idx][1], DEFAULT_CONFIG[correlated_idx]])

            configs.append(c)
        # print("test", configs)
        scored = []
        for c in configs:
            out = get_setpoint(c, PLANS)
            fv = compute_fitness(out, PLANS)
            rapid_score = fv["interruption"]
            scored.append((rapid_score, c))

        scored.sort(reverse=True, key=lambda x: x[0])
        seeds = scored[:K]

        seed_values = [c[target_idx] for _, c in seeds]
        new_low = min(seed_values)
        new_high = max(seed_values)
        span = new_high - new_low
        low = new_low - 0.5 * span
        high = new_high + 0.5 * span

        for s, c in seeds:
            candidates.append(c)
            candidate_scores.append(s)

    return candidates, candidate_scores


if __name__ == "__main__":
    result, scores = mutate_nd_for_rapid(1,2)
    for r,s in zip(result, scores):
        print(s, r)