import config
import mission
import random
import GArandomFuzz


def get_random_value_with_step(ranges, step):
    valid_values = []

    # 遍历每个区间范围
    for low, high in ranges:
        # 从 low 到 high 生成符合步长的值
        current = low
        while current <= high:
            valid_values.append(round(current, 6))  # 避免浮点数问题，保留适当小数位数
            current += step

    # 从所有符合步长的值中随机选择一个
    return random.choice(valid_values)


def mutated_value_param(config_combination, config_single, config_default, step_size, n):
    mutated_combinations = []

    # 遍历组合中的每个目标参数
    for target_param, dependent_params in config_combination.items():
        # 获取 target_param 的范围列表
        target_ranges = config_single[target_param]
        target_step = step_size[target_param]

        # 生成n个符合步长的target值
        target_values = [get_random_value_with_step(target_ranges, target_step) for _ in range(n)]

        # 为每个生成的target_value创建变异组合
        for target_value in target_values:
            mutated_combination = {target_param: target_value}

            # 为每个 dependent_param 生成一个值（从最小值、最大值和默认值中随机选择）
            for dep_param in dependent_params:
                dep_ranges = config_single[dep_param]
                dep_default_value = config_default.get(dep_param)

                # 获取 dependent_param 的最小值、最大值和默认值
                dep_value = get_random_boundary_or_default_value(dep_ranges, dep_default_value)

                # 添加到组合中
                mutated_combination.update({dep_param: dep_value})

            mutated_combinations.append(mutated_combination)

    return mutated_combinations


'''
初始化5个种子
'''
def mutate_multiple_params_with_random_target(config_combination, config_single, config_default, step_size, n=5):
    mutated_combinations = []

    # 遍历组合中的每个目标参数
    for target_param, dependent_params in config_combination.items():
        # 获取 target_param 的范围列表
        target_ranges = config_single[target_param]
        target_step = step_size[target_param]

        target_values = get_unique_random_values_with_step(target_ranges, target_step, n)


        # 为每个生成的 target_value 创建一个变异组合
        for target_value in target_values:
            mutated_combination = {target_param: target_value}

            # 为每个 dependent_param 生成一个值（最小值、最大值或默认值随机选择）
            for dep_param in dependent_params:
                dep_ranges = config_single[dep_param]
                dep_default_value = config_default.get(dep_param)
                # dep_default_value = config.combination.get(dep_param)
                # print("dep param:",dep_param,dep_ranges,dep_default_value)

                # 获取 dependent_param 的最小值、最大值和默认值
                dep_value = get_random_boundary_or_default_value(dep_ranges, dep_default_value)

                # 添加到组合中
                mutated_combination.update({dep_param: dep_value})

            mutated_combinations.append(mutated_combination)

    return mutated_combinations


def get_unique_random_values_with_step(ranges, step_size, n):
    """
    在范围内生成 n 个不重复的随机值，并按照步长调整为整数倍。
    """
    unique_values = set()
    for _ in range(n):
        random_value = get_random_value_with_step(ranges, step_size)

        # 如果生成的值不在集合中，则加入
        if random_value not in unique_values:
            unique_values.add(random_value)


    return list(unique_values)

def get_random_value_with_step(ranges, step_size):
    """
    在范围内随机生成一个值，并按照步长调整为整数倍。
    """
    all_values = []
    for r in ranges:
        min_value, max_value = r
        # 生成在范围内的随机值
        random_value = random.uniform(min_value, max_value)
        # 调整为步长的整数倍
        stepped_value = round(random_value / step_size) * step_size
        all_values.append(stepped_value)

    # 从所有随机值中选择一个
    return random.choice(all_values)

'''
max min default
'''
def get_random_boundary_or_default_value(ranges, default_value):
    """
    随机选择最小值、最大值或默认值之一
    """

    value = []

    min_value = min(r[0] for r in ranges)  # 最小值
    max_value = max(r[1] for r in ranges)  # 最大值
    value.append(max_value)
    value.append(min_value)
    value.append(default_value)

    return random.choice(value)

'''
mutated_combinations 变成configuration 
getdll 测试
'''
def update_configuration_with_combination(default_config, mutated_combination):
    """
    将 mutated_combination 中的参数值更新到默认的 configuration 中。
    """
    updated_config = default_config.copy()
    updated_config.update(mutated_combination)  # 只更新变异的参数
    return updated_config


def multi_mutation():

    result = []
    for param in config.configuration_default:
#         对当前配置残生生成n个种子 主配置随机 dep 三个值
        mutatd_value = mutated_value_param(param)


def mutate_and_optimize_multiple_params(config_combination, config_single, config_default, step_size, n=5, m=5, threshold=0.7, iterations=10):
    # 初始化五个种子（mutated_combinations）
    mutated_combinations = mutate_multiple_params_with_random_target(config_combination, config_single, config_default,
                                                                     step_size, n)
    print("mutation:",mutated_combinations)
    # 构建完整的 configuration 列表，初始值为默认配置
    configurations = [update_configuration_with_combination(config.configuration, combination) for combination in
                      mutated_combinations]


    # for iteration in range(iterations):
    #     # 计算每个组合的适应度分数
    #     fitness_scores = [(config, GArandomFuzz.getDll(config,mission.commandNum21,mission.commands21)) for config in configurations]
    #
    #     # 适应度降序排序
    #     fitness_scores.sort(key=lambda x: x[1], reverse=True)
    #
    #     # 筛选出适应度大于阈值的组合
    #     filtered_results = [item for item in fitness_scores if item[1] > threshold]
    #
    #     if not filtered_results:
    #         print("没有满足阈值的组合")
    #         break
    #
    #     # 输出当前最佳组合和适应度分数
    #     print(
    #         f"Iteration {iteration + 1}, best configuration: {filtered_results[0][0]}, fitness score: {filtered_results[0][1]}")
    #
    #     # 在适应度最高的组合附近继续变异生成 m 个新的组合
    #     new_combinations = []
    #     for result in filtered_results[:m]:  # 只对前 m 个组合继续变异
    #         best_combination = extract_combination_from_config(result[0], config_combination)
    #
    #         for _ in range(m):
    #             # 对每个 target_param 和 dependent_param 进行±50%的变异，并检查是否符合步长和范围
    #             new_combination = mutate_nearby_combination(best_combination, config_single, step_size)
    #             if new_combination and new_combination not in new_combinations:
    #                 new_combinations.append(new_combination)
    #
    #     # 更新 configuration 列表为新的组合
    #     configurations = [update_configuration_with_combination(config_default, combination) for combination in
    #                       new_combinations]
    #
    # return filtered_results

def extract_combination_from_config(config, combination_structure):
    """
    从完整的 configuration 中提取当前变异涉及的组合部分。
    """
    extracted_combination = {param: config[param] for param in combination_structure.keys()}
    return extracted_combination


def mutate_nearby_combination(best_combination, config_single, step_size):
    """
    在最佳组合的参数附近继续变异，并确保变异后的值符合步长和范围。
    """
    new_combination = {}

    for param, best_value in best_combination.items():
        # 获取参数的范围和步长
        ranges = config_single[param]
        step = step_size[param]

        # 生成±50%的变异
        variation_range = best_value * 0.5
        random_variation = random.uniform(-variation_range, variation_range)
        stepped_variation = round(random_variation / step) * step
        new_value = best_value + stepped_variation

        # 检查变异值是否在参数的范围内，超出范围则丢弃该组合
        if not is_within_ranges(new_value, ranges):
            return None

        # 如果符合条件，将新的参数值添加到新的组合中
        new_combination[param] = new_value

    return new_combination


def is_within_ranges(value, ranges):
    """
    检查值是否在参数的不连续范围内。
    """
    for min_val, max_val in ranges:
        if min_val <= value <= max_val:
            return True
    return False



if __name__ == '__main__':
    # result = mutate_multiple_params_with_random_target(config.combination,config.configuration_single,config.configuration_default,config.configuration_step)
    # config_combination, config_single, config_default, step_size, n = 5, m = 5, threshold = 0.7, iterations = 10
    result = mutate_and_optimize_multiple_params(config.combination,config.configuration_single,config.configuration_default,config.configuration_step)

    print(result)