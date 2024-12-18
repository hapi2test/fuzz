
import config
import mission
import GArandomFuzz
import sys


def one_dimensional_mutation(missionNum,mission, param,default_value,default_range):
    # Perform upper-bound search
    Rmax = one_mutation(missionNum,mission, param,default_value,default_range, bound='U')
    # Perform lower-bound search
    Rmin = one_mutation(missionNum,mission, param,default_value,default_range, bound='L')
    return Rmax, Rmin


def one_mutation(missionNum,mission, param,default_value,default_range, bound):
    P_default = default_value
    P_min = default_range[0]
    P_max = default_range[1]

    if bound == 'U':  # Upper-bound search
        test_value = (P_max + P_default) / 2
        max_limit = P_max
        min_limit = P_default
    else:  # Lower-bound search
        test_value = (P_default + P_min) / 2
        max_limit = P_default
        min_limit = P_min

    MinDiff = 0.1  # Minimum difference to stop binary search
    prev_test_value = None  # Store the previous test value for exit condition

    # 第一次检查边界
    config_mutated = update_config(param, test_value)
    warning_len = GArandomFuzz.warning_count(config_mutated, missionNum, mission)
    if bound =='U' and warning_len==0:
        return P_max
    elif bound =='L' and warning_len==0:
        return P_min

    # while True:
    #     # Run evaluation or deviation check
    #     config_mutated = update_config(param,test_value)
    #     warning_len = GArandomFuzz.warning_count(config_mutated,missionNum,mission)
    #
    #     if bound == 'U' and warning_len!=0:
    #         max_limit = test_value
    #     elif bound == 'U' and warning_len==0:
    #         return test_value
    #     elif bound =='L' and warning_len!=0:
    #         min_limit = test_value
    #     elif bound =='L' and warning_len==0:
    #         return test_value
    #     test_value = (max_limit + min_limit) / 2  # Update test value
    while prev_test_value is None or abs(test_value - prev_test_value) > MinDiff:
        prev_test_value = test_value
        # Run evaluation by counting warnings
        config_mutated = update_config(param, test_value)
        warning_len = GArandomFuzz.warning_count(config_mutated, missionNum, mission)

        if bound == 'U':
            if warning_len != 0:
                max_limit = test_value  # Move upper bound down
            else:
                min_limit = test_value  # Move lower bound up
        else:  # Lower-bound search ('L')
            if warning_len != 0:
                min_limit = test_value  # Move lower bound up
            else:
                max_limit = test_value  # Move upper bound down

        test_value = (max_limit + min_limit) / 2  # Update test value

        # Return the final valid bound
    return test_value


def update_config(param,value):
    temp = config.configuration.copy()
    temp[param] = value
    return temp


def test():
    for param,value in config.config_rvfuzz.items():
        default_value = value[0]
        default_range = value[1]

        Rmax,Rmin = one_dimensional_mutation(mission.commandNum21,mission.commands21,param,default_value,default_range)
        print(f"param:{param},Rmax:{Rmax},Rmin:{Rmin}")

if __name__ == '__main__':

    f = open('rvfuzz.txt','w')
    sys.stdout = f
    test()
    f.flush()