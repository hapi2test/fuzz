import config
import GArandomFuzz
import mission
import sys
import time
import random
import mutation
import random


def mutated_value_param(tartget_single, target_step, num):
    min_value = min(r[0] for r in tartget_single)  # 最小值
    max_value = max(r[1] for r in tartget_single)  # 最大值

    value = set()
    for _ in range(num):
        random_value = random.uniform(min_value, max_value)
    # 调整为步长的整数倍
        stepped_value = round(random_value / target_step) * target_step
        value.add(stepped_value)
    return value




def update_configuration(param, mutated_value, current_config):
    # 将 mutated_value 更新到 current_config 中
    updated_config = current_config.copy()
    updated_config[param] = mutated_value

    return updated_config


def get_random_boundary_or_default_value(ranges, default_value):
    # 获取范围内的最大值和最小值
    min_value = min([r[0] for r in ranges])
    max_value = max([r[1] for r in ranges])

    # 随机从最大值、最小值和默认值中选择一个
    return random.choice([min_value, max_value, default_value])


def update_configuration_multi(target_param, value, dep_param, dep_value, current_configu):
    update_config = current_configu.copy()
    update_config[target_param] =value
    update_config[dep_param] = dep_value

    return update_config



def perform_mutation_and_selection(num, threshold, iterations,flag):
    results = []

    for target_param, dep_params in config.combination.items():

        config_default = config.configuration_default.copy()

        target_single = config.configuration_single[target_param]
        target_step = config.configuration_step[target_param]
        target_values = mutated_value_param(
            target_single,
            target_step,
            num
        )

        fitness_scores = {}
        # 遍历每个 target 变异值
        for target_value in target_values:
            # 更新 target 参数的值
            mutated_config = update_configuration(target_param, target_value, config.configuration)

            dep_range = config.configuration_single[dep_params]
            dep_default = config.configuration_default[dep_params]
            dep_value = get_random_boundary_or_default_value(dep_range, dep_default)

            mutated_config = update_configuration(dep_params, dep_value, mutated_config)

            score = GArandomFuzz.getDll(mutated_config, mission.commandNum21, mission.commands21,flag)

            fitness_scores[(target_param, target_value, dep_params, dep_value)] = score

        # 对变异值按适应度分数进行排序
        sorted_fitness_scores = sorted(fitness_scores.items(), key=lambda x: x[1], reverse=True)

        # 只保留适应度分数大于阈值的变异值
        for (target_param, target_value, dep_param, dep_value), score in sorted_fitness_scores:
            if score >= threshold:
                results.append({
                    'target_param': target_param,
                    'target_value': target_value,
                    'dep_param': dep_param,
                    'dep_value': dep_value,
                    'fitness score': score
                })

    final_results = []
    final_results.append(results)

    for _ in range(iterations):
        if not results:  # 如果没有符合条件的结果，跳出循环
            break

        # 从结果中选择适应度最高的结果
        best_result = results.pop(0)  # 获取并移除适应度最高的结果
        target_param = best_result['target_param']
        target_value = best_result['target_value']
        dep_param = best_result['dep_param']
        dep_value = best_result['dep_value']

        # 计算变异值的范围
        variation_range_min = target_value * 0.5  # 可调整的范围
        variation_range_max = target_value * 1.5
        step_size = config.configuration_step[target_param]

        # 生成5个新的变异值
        nearby_mutated_values = set()
        for _ in range(5):
            random_variation = random.uniform(variation_range_min, variation_range_max)
            stepped_variation = round(random_variation / step_size) * step_size
            new_value = stepped_variation

            # 检查变异值是否在目标范围内
            for min_value, max_value in config.configuration_single[target_param]:
                if min_value <= new_value <= max_value:
                    nearby_mutated_values.add(new_value)
                    break  # 一旦找到合适区间，直接退出当前区间检查

        # 计算新变异值的适应度
        for value in nearby_mutated_values:
            mutated_config = update_configuration_multi(target_param, value,dep_param,dep_value, config.configuration)
            score = GArandomFuzz.getDll(mutated_config, mission.commandNum21, mission.commands21,flag)

            if score >= threshold:
                final_results.append({
                    'target_param': target_param,
                    'target_value': value,
                    'dep_param': dep_param,
                    'dep_value': dep_value,
                    'fitness score': score
                })

    return final_results


def shrink_ranges(final_results, configuration_single, configuration_step):
    new_ranges = {}



    target_values = {entry['target_param']: entry['target_value'] for entry in final_results[0]}


    for param, value in target_values.items():
        if param in configuration_single:
            # 获取 single 中的范围
            single_range = configuration_single[param]
            # 删除 single_range 中的 value
            updated_range = [(min_val, max_val) for min_val, max_val in single_range if
                             not (min_val <= value <= max_val)]

            # 计算新的连续范围
            continuous_ranges = []
            step_size = configuration_step[param]
            current_range = []

            for min_val, max_val in updated_range:
                if not current_range:
                    current_range = [min_val, max_val]
                elif min_val <= current_range[1] + step_size:
                    current_range[1] = max(max_val, current_range[1])
                else:
                    continuous_ranges.append(tuple(current_range))
                    current_range = [min_val, max_val]

            if current_range:
                continuous_ranges.append(tuple(current_range))

            # 更新新的范围
            new_ranges[param] = continuous_ranges if len(continuous_ranges) > 0 else single_range
        else:
            new_ranges[param] = configuration_single[param]

    return new_ranges


if __name__ == '__main__':

    f = open('cmdOutput.txt','w')
    sys.stdout = f

    time_start = time.time()
    result = perform_mutation_and_selection(100, 0.5, 200,2)
    time_point = time.time()
    bound = shrink_ranges(result,config.configuration_single,config.configuration_step)
    time_end = time.time()
    print(bound)
    print("mutation time:",time_point-time_start,"bound time:",time_end - time_point)
    f.flush()

