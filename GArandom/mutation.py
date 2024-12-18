import config
import GArandomFuzz
import random
import mission
import sys
import time

'''
生成随机值
'''
def mutate(param_name, default_value, step_size, value_range,num):
    mutated_values = set()  # 使用集合来存储唯一的变异值
    num_steps = int((value_range[1] - value_range[0]) / step_size)

    for _ in range(num):
    # while len(mutated_values) < num:
        # 随机选择一个步数
        step = random.randint(-num_steps, num_steps)
        mutation = default_value + step * step_size

        # 确保变异值在合法范围内
        mutation = max(min(mutation, value_range[1]), value_range[0])

        # 添加到集合中以保证唯一性
        mutated_values.add(mutation)

    return list(mutated_values)  # 转换回列表返回


def update_configuration(param_name, mutated_value, config):

    # 创建一个新的配置字典，包含变异值
    new_config = config.copy()
    new_config[param_name] = mutated_value
    # 返回更新后的配置
    return new_config  # 使用生成器返回每个新配置

'''
初始化5个随机值 计算适应度分数
保留大于阈值的
返回 值和fitness score
'''
def perform_mutation_and_selection(num, threshold,iterations,flag):
    results = []

    for param in config.configuration_default:

        # 初始化配置为默认值
        config_default = config.configuration_default.copy()
        # 对当前参数进行n次变异
        mutated_values = mutate(param, config_default[param], config.configuration_step[param], config.configuration_init[param],num)


        fitness_scores = {}
        for mutated_value in mutated_values:
            mutated_config = update_configuration(param,mutated_value,config.configuration)
            score = GArandomFuzz.getDll(mutated_config,mission.commandNum21,mission.commands21,flag)
            fitness_scores[mutated_value] = score
        # print(fitness_scores)
        sorted_fitness_scores = sorted(fitness_scores.items(), key=lambda x: x[1], reverse=True)

        for value, score in sorted_fitness_scores:
            if score > threshold:
                results.append({param: value, 'fitness score': score})  # 构建包含param, value, 和 score的字典

    final_result =[]
    final_result.append(results)

    for _ in range(iterations):
        # 针对results中适应度分数最高的值进行变异
        if not results:  # 如果没有符合条件的结果，跳出循环
            break

        # 在最佳值附近生成5个新的变异值
        best_result = results.pop(0)
        param_name = list(best_result.keys())[0]  # 获取参数名
        best_value = best_result[param_name]  # 获取最佳变异值
        # print("best", param_name, best_value)  # 输出最佳值以进行调试

        variation_range_min = best_value * 0.5  # 最小范围
        variation_range_max = best_value * 1.5  # 最大范围
        step_size = config.configuration_step[param_name]  # 获取步长

        # 在best_value附近生成5个新的变异值，以step为单位调整
        nearby_mutated_values = set()
        for _ in range(5):
            random_variation = random.uniform(variation_range_min, variation_range_max)
            stepped_variation = round(random_variation / step_size) * step_size  # 调整为步长的整数倍
            new_value = stepped_variation  # 使用生成的变异值

            # 检查变异值是否在配置参数的范围内，超出范围则舍弃
            min_value, max_value = config.configuration_init[param_name]  # 获取配置参数的范围
            if min_value <= new_value <= max_value and new_value not in nearby_mutated_values:
                nearby_mutated_values.add(new_value)

        # 计算新变异值的适应度
        nearby_fitness_scores = {}
        for value in nearby_mutated_values:

            mutated_config = update_configuration(param, value, config.configuration)
            score = GArandomFuzz.getDll(mutated_config, mission.commandNum21, mission.commands21,flag)  # 计算适应度分数
            if score is not None:  # 确保适应度分数不是None
                nearby_fitness_scores[value] = score  # 将变异值和适应度分数对应起来

        # 按照适应度分数降序排序
        sorted_nearby_fitness_scores = sorted(nearby_fitness_scores.items(), key=lambda x: x[1], reverse=True)

        # 只保留适应度分数大于阈值x的值，并加入results
        for value, score in sorted_nearby_fitness_scores:
            if score > threshold:
                results.append({param: value, 'fitness score': score})  # 添加到results中
                final_result.append({param: value, 'fitness score': score})
    return final_result


def shrink_init_range_by_results(config_init, results, step_size):
    new_bounds = {}

    for param_name in config_init:
        # 获取原始的范围和步长
        min_value, max_value = config_init[param_name]
        step = step_size[param_name]

        # 获取 results 中已经生成的值
        values_in_result = [entry[param_name] for entry in results if param_name in entry]

        # 初始化 remaining_values 列表，表示 min_value 到 max_value 的所有步长倍数
        all_possible_values = [round(min_value + i * step, 10) for i in range(int((max_value - min_value) // step) + 1)]

        # 排除已经在 results 中的值，剩下的就是未使用的值
        remaining_values = sorted(set(all_possible_values) - set(values_in_result))

        if not remaining_values:  # 如果没有剩余的区间，跳过这个参数
            continue

        # 找到不连续的剩余区间
        consecutive_ranges = []
        start = remaining_values[0]
        for i in range(1, len(remaining_values)):
            # 如果当前值和前一个值不是连续的，则认为是新的一段范围
            if remaining_values[i] != remaining_values[i - 1] + step:
                end = remaining_values[i - 1]
                consecutive_ranges.append((start, end))
                start = remaining_values[i]
        # 添加最后一段连续范围
        consecutive_ranges.append((start, remaining_values[-1]))

        # 过滤出长度大于2倍step size的连续区间
        filtered_ranges = [(start, end) for start, end in consecutive_ranges if end - start >= 10 * step]

        # 如果有符合条件的范围，选择第一个作为新的bound
        if filtered_ranges:
            new_bounds[param_name] = filtered_ranges

    return new_bounds




if __name__ == '__main__':
    f = open('cmdOutput.txt', 'w')
    sys.stdout = f

    time_start = time.time()
    result = perform_mutation_and_selection(100,0.7,200,0)

    time_point = time.time()

    bound = shrink_init_range_by_results(config.configuration_init,result,config.configuration_step)
    time_end =time.time()

    print(bound)

    print("mutation time:",time_point-time_start,"bound time:",time_end-time_point)
    f.flush()
