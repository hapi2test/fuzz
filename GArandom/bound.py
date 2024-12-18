from sys import stdout

import GArandomFuzz
import mutation
import config
import test
import sys


def inter_bound(result1, result2, result3):
    intersection_result = {}

    # 获取三个结果中的所有参数（包括非公共参数）
    all_params = set(result1.keys()) | set(result2.keys()) | set(result3.keys())

    # 遍历每个参数
    for param in all_params:
        bounds1 = result1.get(param, None)
        bounds2 = result2.get(param, None)
        bounds3 = result3.get(param, None)

        # 存在该参数时，计算范围交集
        if bounds1 and bounds2 and bounds3:
            combined_intersections = []
            for bound1 in bounds1:
                for bound2 in bounds2:
                    for bound3 in bounds3:
                        # 计算三个bound的交集，按最大下限和最小上限取值
                        lower_bound = max(bound1[0], bound2[0], bound3[0])
                        upper_bound = min(bound1[1], bound2[1], bound3[1])

                        # 交集有效时，加入结果
                        if lower_bound <= upper_bound:
                            combined_intersections.append((lower_bound, upper_bound))

            # 如果有有效交集，更新结果为交集，否则保留原值
            if combined_intersections:
                intersection_result[param] = combined_intersections
            else:
                # 如果没有有效交集，保留第一个result的范围
                intersection_result[param] = bounds1

        # 如果某个参数不在其中某个result中，保留已有的范围
        elif bounds1:
            intersection_result[param] = bounds1
        elif bounds2:
            intersection_result[param] = bounds2
        elif bounds3:
            intersection_result[param] = bounds3

    return intersection_result




def climb_bound_single():
    result = mutation.perform_mutation_and_selection(100, 4, 200, 0)

    bound = mutation.shrink_init_range_by_results(config.configuration_init, result, config.configuration_step)
    return bound

def  deviation_bound_single():
    result = mutation.perform_mutation_and_selection(100, 0.06, 200, 1)

    bound = mutation.shrink_init_range_by_results(config.configuration_init, result, config.configuration_step)
    return bound


def  interruption_bound_single():
    result = mutation.perform_mutation_and_selection(100, 0.7, 200, 2)

    bound = mutation.shrink_init_range_by_results(config.configuration_init, result, config.configuration_step)
    return bound

def clime_bound_multi():
    result = test.perform_mutation_and_selection(100, 4, 200,0)
    bound = test.shrink_ranges(result, config.configuration_single, config.configuration_step)

    return bound
def deviation_bound_multi():
    result = test.perform_mutation_and_selection(100, 0.05, 200, 1)
    bound = test.shrink_ranges(result, config.configuration_single, config.configuration_step)

    return bound

def interruption_bound_multi():
    result = test.perform_mutation_and_selection(100, 0.5, 200, 2)
    bound = test.shrink_ranges(result, config.configuration_single, config.configuration_step)

    return bound



if __name__ == '__main__':
    # result1 = climb_bound_single()
    # result2 = deviation_bound_single()
    # result3 = interruption_bound_single()
    # inter_bound = inter_bound(result1, result2, result3)
    f = open('test.txt','w')
    sys.stdout = f
    result1 = clime_bound_multi()
    print(result1)
    result2 = interruption_bound_multi()
    print(result2)
    result3 = interruption_bound_multi()
    print(result3)
    inter_bound = inter_bound(result1, result2, result3)

    print(inter_bound)

    f.flush()