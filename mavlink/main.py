import threading
import time

import px4
from run_time import *
from px4 import *
from analysisLog import *
import os
import subprocess
from parmStruct import *
from paramSM import *
from paramDefualt import *

def get_log():
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
    log_path = "/home/gazebo/Desktop/px4Test/"+log_name
    return log_path



def px4_main():
    mission_list = [
        (47.3977419, 8.5455940, 15),
        (47.3979690, 8.5459728, 15),
        (47.3979552, 8.5452020, 15)
    ]
    config_dict1 = {
        # 'MIS_DIST_1WP': 900,
        # 'MIS_YAW_TMT': -1,
        # 'MPC_LAND_ALT1': 10,
        # 'MPC_XY_VEL_ALL': -10,
        'MPC_TILTMAX_LND': 12
    }

    score_list = [0, 0, 0]

    runTime1 = runTime(mission_list, config_dict1, score_list)
    # runTime2 = runTime(mission_list, config_dict2,score_list)
    # runTime_lists = [runTime1,runTime2]
    runTime_lists = [runTime1]

    for runTime_list in runTime_lists:
        # mission start
        # 获取log的位置
        px4.px4_conect(runTime_list.config_dict,runTime_list.mission_list)


def mutation_multi_config():
    mission_list = [
        (47.3977419, 8.5455940, 15),
        (47.3979690, 8.5459728, 10),
        (47.3979552, 8.5452020, 10),
        (47.3979611, 8.5458973, 7),
        (47.3980167, 8.5464210, 7),
        (47.3976268, 8.5460387, 5),
        (47.3976888, 8.5469342, 5),
        (47.3976817, 8.5457166, 10),
        (47.3975346, 8.5456459, 10),
        (47.3976959, 8.5455071, 5),
    ]
    score_list = [0, 0, 0]
    paramsm = paramSMulti('MPC_XY_VEL_ALL','MPC_XY_VEL_MAX',[10,-10,6],[20,20,12])
    # paramsm = paramSMulti('MPC_XY_VEL_ALL', 'MPC_XY_VEL_MAX', [-20,-35,-12,0,1,-1,10,20,35,50], [20, 20, 12,0,12,0,20,12,0,20])
    scoreList = []
    for i in range(paramsm.get_num()):
        print("--------------------start {0} param set-----------------------------".format(i))
        # print(paramS1.get_value(i))
        runTimetemp = runTime(mission_list, paramsm.get_dict(i), score_list)
        flag = px4.px4_conect(runTimetemp.config_dict, runTimetemp.mission_list)
        # analysis log
        log_path = get_log()
        #
        # # analysis logs
        score_deviation, score_rapi, score_interruption = analyis_ulog(log_path)
        if flag == True:
            runTimetemp.set_score(score_deviation, score_rapi, 1)
        else:
            runTimetemp.set_score(score_deviation, score_rapi, 0)
        scoreList.append((score_deviation, score_rapi, score_interruption))
        # 输出每个config 对应的score
        # scoreList.append(runTimetemp.score_list)
        runTimetemp.get_score_list_print()

    # score list
    for i in scoreList:
        print(i)
def mutation_one_config():
    mission_list = [
        (47.3977419, 8.5455940, 15),
        (47.3979690, 8.5459728, 10),
        (47.3979552, 8.5452020, 10),
        (47.3979611, 8.5458973, 7),
        (47.3980167, 8.5464210, 7),
        (47.3976268, 8.5460387, 5),
        (47.3976888, 8.5469342, 5),
        (47.3976817, 8.5457166, 10),
        (47.3975346, 8.5456459, 10),
        (47.3976959, 8.5455071, 5),
    ]
    score_list = [0, 0, 0]
    # paramS1 = ParmS('MPC_TILTMAX_LND', [4, 5, 6,])
    paramS1 = ParmS('MPC_TILTMAX_LND',[4,5,6,89,90,94,100,0,-1,50,52,232,245,367])
    paramS2 = ParmS('MPC_XY_VEL_ALL',[-20,-35,-12,0,1,-1,10,20,35,50])
    scoreList = []
    for i in range(paramS1.get_num()):
        print("--------------------start {0} param set-----------------------------".format(i))
        # print(paramS1.get_value(i))
        runTimetemp = runTime(mission_list, paramS1.get_value(i), score_list)
        # mission start
        # 获取log的位置
        flag = px4.px4_conect(runTimetemp.config_dict, runTimetemp.mission_list)

        # analysis log
        log_path = get_log()
        #
        # # analysis logs

        score_deviation, score_rapi, score_interruption = analyis_ulog(log_path)
        if flag == True:
            runTimetemp.set_score(score_deviation, score_rapi, 1)
        else:
            runTimetemp.set_score(score_deviation, score_rapi, 0)
        scoreList.append((score_deviation, score_rapi, score_interruption))
        # 输出每个config 对应的score
        # scoreList.append(runTimetemp.score_list)
        runTimetemp.get_score_list_print()

    # score list
    for i in scoreList:
        print(i)
def run_param():
    mission_list = [
        (47.3977419, 8.5455940, 15),
        (47.3979690, 8.5459728, 10),
        (47.3979552, 8.5452020, 10),
        (47.3979611, 8.5458973, 7),
        (47.3980167, 8.5464210, 7),
        (47.3976268, 8.5460387, 5),
        (47.3976888, 8.5469342, 5),
        (47.3976817, 8.5457166, 10),
        (47.3975346, 8.5456459, 10),
        (47.3976959, 8.5455071, 5),
    ]
    score_list = [0, 0, 0]
    # paramS1 = ParmS('MPC_TILTMAX_LND', [4, 5, 6,])
    paramS1 = ParmS('MC_PITCHRATE_MAX', [150,180])
    scoreList = []
    for i in range(paramS1.get_num()):
        print("--------------------start {0} param set-----------------------------".format(i))
        # print(paramS1.get_value(i))
        runTimetemp = runTime(mission_list, paramS1.get_value(i), score_list)
        # mission start
        # 获取log的位置
        flag = px4.px4_conect(runTimetemp.config_dict, runTimetemp.mission_list)

        # analysis log
        log_path = get_log()
        #
        # # analysis logs

        score_deviation, score_rapi, score_interruption = analyis_ulog(log_path)
        if flag == True:
            runTimetemp.set_score(score_deviation, score_rapi, 1)
        else:
            runTimetemp.set_score(score_deviation, score_rapi, 0)
        scoreList.append((score_deviation, score_rapi, score_interruption))
        # 输出每个config 对应的score
        # scoreList.append(runTimetemp.score_list)
        runTimetemp.get_score_list_print()


        time.sleep(60)

    # score list
    for i in scoreList:
        print(i)


def test_log():
    path = '04_41_05.ulg'
    score1,score2,score3 = analyis_ulog(path)
    print(score1,score2,score3)

if __name__ == '__main__':
    # mutation_multi_config()
    # run_param()
    # test()
    # px4.upload_default_config()
    # mutation_one_config()
    # run_param()
    test_log()
'''
if __name__ == '__main__':
    start_time = time.time()

    mission_list = [
        (47.3977419, 8.5455940, 15),
        (47.3979690, 8.5459728, 10),
        (47.3979552, 8.5452020, 10),
        (47.3979611,8.5458973,7),
        (47.3980167,8.5464210,7),
        (47.3976268,8.5460387,5),
        (47.3976888,8.5469342,5),
        (47.3976817,8.5457166,10),
        (47.3975346,8.5456459,10),
        (47.3976959,8.5455071,5),
    ]
    config_dict1 = {
        'MPC_TILTMAX_LND': 12
    }
    config_dict2 = {
        'MPC_TILTMAX_LND': 10
    }
    config_dict3 = {
        'MPC_TILTMAX_LND': 4
    }
    config_dict4 = {
        'MPC_TILTMAX_LND': 3
    }
    config_dict5 = {
        'MPC_TILTMAX_LND': 9
    }
    config_dict6 = {
        'MPC_TILTMAX_LND': 8
    }
    config_dict7 = {
        'MPC_TILTMAX_LND': 2
    }
    config_dict8 = {
        'MPC_TILTMAX_LND': 15
    }
    score_list =[0,0,0]

    runTime1 = runTime(mission_list, config_dict1,score_list)
    runTime2 = runTime(mission_list, config_dict2,score_list)
    runTime3 = runTime(mission_list, config_dict3,score_list)
    runTime4 = runTime(mission_list, config_dict4,score_list)
    runTime5 = runTime(mission_list, config_dict5, score_list)
    runTime6 = runTime(mission_list, config_dict6, score_list)
    runTime7 = runTime(mission_list, config_dict7, score_list)
    runTime8 = runTime(mission_list, config_dict8, score_list)

    runTime_lists = [runTime1,runTime2,runTime3,runTime4,runTime5,runTime6,runTime7,runTime8]


    for runTime_list in runTime_lists:
        # mission start
        # 获取log的位置
        px4.px4_conect(runTime_list.config_dict,runTime_list.mission_list)

        # analysis log
        log_path = get_log()
        #
        # # analysis logs
        score_deviation, score_rapi, score_interruption = analyis_ulog(log_path)
        runTime_list.set_score(score_deviation, score_rapi, score_interruption)



    # 输出每个config 对应的score
    for runTime_list in runTime_lists:
        runTime_list.get_score_list()


    print("total time:",time.time()-start_time)

'''









