import numpy as np

'''
配置参数列表和步长
'''

configuration_step = {
    'SYS_VEHICLE_RESP': 0.05,
    'MPC_ACC_HOR': 1,
    'MPC_ACC_HOR_MAX': 1,
    'MPC_TILTMAX_AIR': 1,
    'MPC_ACC_DOWN_MAX': 1,
    'MPC_ACC_UP_MAX': 1,
    'MPC_JERK_MAX': 1,
    'MPC_JERK_AUTO': 1,
    'MPC_XY_VEL_ALL': 1,
    'MPC_XY_CRUISE': 1,
    'MPC_XY_VEL_MAX': 1,
    'MPC_Z_VEL_ALL': 0.5,
    'MPC_Z_V_AUTO_UP': 0.5,
    'MPC_Z_VEL_MAX_UP': 0.1,
    'MPC_Z_V_AUTO_DN': 0.5,
    'MPC_Z_VEL_MAX_DN': 0.1,
    'MPC_TKO_SPEED': 0.5,
    'MPC_LAND_SPEED': 0.1,
    'MPC_TILTMAX_LND': 1,
    'MPC_THR_HOVER':0.01,
    'MPC_THR_MAX': 0.05,
    'MPC_THR_MIN': 0.01,
    'MC_PITCHRATE_MAX': 5,
    'MIS_YAW_ERR': 1,
    'MPC_YAWRAUTO_MAX': 5
}

'''
config default
'''
configuration_default = {
    'SYS_VEHICLE_RESP': -0.4,
    'MPC_ACC_HOR': 3,
    'MPC_ACC_HOR_MAX': 5,
    'MPC_TILTMAX_AIR': 45,
    'MPC_ACC_DOWN_MAX': 3,
    'MPC_ACC_UP_MAX': 4,
    'MPC_JERK_MAX': 8,
    'MPC_JERK_AUTO': 4,
    'MPC_XY_VEL_ALL': -10,
    'MPC_XY_CRUISE': 5,
    'MPC_XY_VEL_MAX': 12,
    'MPC_Z_VEL_ALL': -3,
    'MPC_Z_V_AUTO_UP': 3,
    'MPC_Z_VEL_MAX_UP': 3,
    'MPC_Z_V_AUTO_DN': 1.5,
    'MPC_Z_VEL_MAX_DN': 1.5,
    'MPC_TKO_SPEED': 1.5,
    'MPC_LAND_SPEED': 0.7,
    'MPC_TILTMAX_LND': 12,
    'MPC_THR_HOVER':0.5,
    'MPC_THR_MAX': 1,
    'MPC_THR_MIN': 0.12,
    'MC_PITCHRATE_MAX': 220,
    'MIS_YAW_ERR': 12,
    'MPC_YAWRAUTO_MAX': 45
}




'''
config range init
'''
configuration_init = {
    "SYS_VEHICLE_RESP":(-1,1),
    "MPC_ACC_HOR": (1, 15),
    "MPC_ACC_HOR_MAX": (2, 15),
    "MPC_TILTMAX_AIR": (20, 89),
    "MPC_ACC_DOWN_MAX":(0.8,15), #
    "MPC_ACC_UP_MAX":(1.0,15),   #
    "MPC_JERK_MAX":(2,50),   #
    "MPC_JERK_AUTO":(1,25),   #
    "MPC_XY_VEL_ALL":(-20,20),   # (-20,20)
    "MPC_XY_CRUISE": (-1, 50),  #(3,20)
    "MPC_XY_VEL_MAX":(0,10),  #(0,20)
    "MPC_Z_VEL_ALL":(-3,999),
    "MPC_Z_V_AUTO_UP":(-1,10),
    "MPC_Z_VEL_MAX_UP":(-1,10),
    "MPC_Z_V_AUTO_DN":(-1,10),
    "MPC_Z_VEL_MAX_DN":(-1,999),
    "MPC_TKO_SPEED":(0,999),
    "MPC_LAND_SPEED":(0,999),
    "MPC_TILTMAX_LND":(0,999),
    "MPC_THR_HOVER":(0,1),
    "MPC_THR_MAX": (-1, 20),
    "MPC_THR_MIN": (-1, 20),
    "MC_PITCHRATE_MAX": (0, 9999),
    "MIS_YAW_ERR":(0,999),
    "MPC_YAWRAUTO_MAX":(-1,999),
}


configuration= {
    'MPC_TKO_RAMP_T': 3, 'MIS_DIST_1WP': 900, 'MIS_YAW_TMT': -1, 'MPC_LAND_ALT1': 10, 'MIS_DIST_WPS': 900,
    'MPC_Z_VEL_MAX_UP': 3, 'MC_PITCHRATE_MAX': 220, 'NAV_MC_ALT_RAD': 0.8, 'MIS_TAKEOFF_ALT': 2.5,
    'MPC_LAND_ALT3': 1,
    'NAV_FW_ALTL_RAD': 5, 'MPC_XY_VEL_MAX': 12, 'MIS_YAW_ERR': 12, 'NAV_FW_ALT_RAD': 10,
    'NAV_ACC_RAD': 5,
    'MPC_YAWRAUTO_MAX': 45, 'MPC_THR_MAX': 1, 'MPC_XY_CRUISE': 5, 'MPC_ACC_DOWN_MAX': 3,
    'MPC_Z_V_AUTO_DN': 1.5,
    'MPC_ACC_UP_MAX': 4, 'MPC_Z_V_AUTO_UP': 3, 'MPC_Z_VEL_MAX_DN': 1.5, 'MPC_TKO_SPEED': 1.5,
    'MPC_TILTMAX_AIR': 45,
    'MPC_JERK_AUTO': 4, 'MPC_ACC_HOR': 3, 'MPC_LAND_SPEED': 0.7, 'MPC_LAND_ALT2': 5, 'MPC_LAND_CRWL': 0.3,
    'MPC_YAW_MODE': 4, 'MC_YAWRATE_MAX': 200, 'MC_YAW_WEIGHT': 0.4, 'MPC_Z_VEL_ALL': -3,
    'SYS_VEHICLE_RESP': -0.4,
    'MPC_ACC_HOR_MAX': 5, 'MPC_JERK_MAX': 8, 'MPC_XY_VEL_ALL': -10, 'MPC_TILTMAX_LND': 12,
    'MPC_THR_HOVER': 0.5,
    'MPC_THR_MIN': 0.2
}

configuration_single={
    'SYS_VEHICLE_RESP': [(-1, 1)],
    'MPC_ACC_HOR': [(1, 15)],
    'MPC_ACC_HOR_MAX': [(2, 15)],
    'MPC_TILTMAX_AIR': [(20, 89)],
    'MPC_ACC_DOWN_MAX': [(0.8, 15)],
    'MPC_ACC_UP_MAX': [(1.0, 15)],
    'MPC_JERK_MAX': [(2, 50)],
    'MPC_JERK_AUTO': [(1, 25)],
    'MPC_XY_VEL_ALL': [(-20, -0.5), (2.5, 20)],
    'MPC_XY_CRUISE': [(2.5, 12.5)],
    'MPC_XY_VEL_MAX': [(4.5, 20)],
    'MPC_Z_VEL_ALL': [(-3, -0.5), (0.5, 5.5)],
    'MPC_Z_V_AUTO_UP': [(-1, -0.5), (0.5, 3.5)],
    'MPC_Z_VEL_MAX_UP': [(2.5, 10)],
    'MPC_Z_V_AUTO_DN': [(-1, np.float64(-0.5)), (np.float64(0.5), np.float64(1.5))],
    'MPC_Z_VEL_MAX_DN': [(np.float64(1.5), 10)],
    'MPC_TKO_SPEED': [(np.float64(0.5), 20)],
    'MPC_LAND_SPEED': [(0, 20)],
    'MPC_TILTMAX_LND': [(0, 45.5)],
    'MPC_THR_HOVER': [(np.float64(0.5), 1)],
    'MPC_THR_MAX': [(0.5, 10)],
    'MPC_THR_MIN': [(-1, np.float64(0.5))],
    'MC_PITCHRATE_MAX': [(0.5, 230)],
    'MIS_YAW_ERR': [(0, 90)],
    'MPC_YAWRAUTO_MAX': [(-1, 360)]
}


# combination = {
#     'MPC_ACC_HOR':['SYS_VEHICLE_RESP'],
#     'MPC_ACC_HOR_MAX':['SYS_VEHICLE_RESP'],
#     'MPC_TILTMAX_AIR':['SYS_VEHICLE_RESP'],
#     'MPC_ACC_DOWN_MAX':['SYS_VEHICLE_RESP'],
#     'MPC_ACC_UP_MAX':['SYS_VEHICLE_RESP'],
#     'MPC_JERK_MAX':['SYS_VEHICLE_RESP'],
#     'MPC_JERK_AUTO':['SYS_VEHICLE_RESP'],
#     'MPC_XY_VEL_ALL':['MPC_XY_VEL_MAX'],
#     'MPC_XY_CRUISE':['MPC_XY_VEL_ALL'],
#     'MPC_XY_VEL_MAX':['MPC_XY_VEL_ALL'],
#     # 'MPC_Z_VEL_ALL':['MPC_Z_V_AUTO_UP','MPC_Z_VEL_MAX_UP','MPC_Z_V_AUTO_DN','MPC_Z_VEL_MAX_DN','MPC_TKO_SPEED','MPC_LAND_SPEED'],
#     'MPC_Z_V_AUTO_UP':['MPC_Z_VEL_ALL'],
#     'MPC_Z_VEL_MAX_UP':['MPC_Z_VEL_ALL'],
#     'MPC_Z_V_AUTO_DN':['MPC_Z_VEL_ALL'],
#     'MPC_Z_VEL_MAX_DN':['MPC_Z_VEL_ALL'],
#     'MPC_TKO_SPEED':['MPC_Z_VEL_MAX_UP'],
#     'MPC_LAND_SPEED':['MPC_Z_VEL_MAX_DN'],
#     # 'MPC_TKO_SPEED':['MPC_Z_VEL_ALL','MPC_Z_VEL_MAX_UP'],
#     # 'MPC_LAND_SPEED':['MPC_Z_VEL_ALL','MPC_Z_VEL_MAX_DN'],
#     'MPC_TILTMAX_LND':['MPC_TILTMAX_AIR'],
#     # 'MPC_THR_HOVER':['MPC_THR_MAX','MPC_THR_MIN'],
#     'MPC_THR_MAX':['MPC_THR_HOVER'],
#     'MPC_THR_MIN':['MPC_THR_HOVER']
# }

combination = {
    'MPC_ACC_HOR':'SYS_VEHICLE_RESP',
    'MPC_ACC_HOR_MAX':'SYS_VEHICLE_RESP',
    'MPC_TILTMAX_AIR':'SYS_VEHICLE_RESP',
    'MPC_ACC_DOWN_MAX':'SYS_VEHICLE_RESP',
    'MPC_ACC_UP_MAX':'SYS_VEHICLE_RESP',
    'MPC_JERK_MAX':'SYS_VEHICLE_RESP',
    'MPC_JERK_AUTO':'SYS_VEHICLE_RESP',
    'MPC_XY_VEL_ALL':'MPC_XY_VEL_MAX',
    'MPC_XY_CRUISE':'MPC_XY_VEL_ALL',
    'MPC_XY_VEL_MAX':'MPC_XY_VEL_ALL',
    # 'MPC_Z_VEL_ALL':['MPC_Z_V_AUTO_UP','MPC_Z_VEL_MAX_UP','MPC_Z_V_AUTO_DN','MPC_Z_VEL_MAX_DN','MPC_TKO_SPEED','MPC_LAND_SPEED'],
    'MPC_Z_V_AUTO_UP':'MPC_Z_VEL_ALL',
    'MPC_Z_VEL_MAX_UP':'MPC_Z_VEL_ALL',
    'MPC_Z_V_AUTO_DN':'MPC_Z_VEL_ALL',
    'MPC_Z_VEL_MAX_DN':'MPC_Z_VEL_ALL',
    'MPC_TKO_SPEED':'MPC_Z_VEL_MAX_UP',
    'MPC_LAND_SPEED':'MPC_Z_VEL_MAX_DN',
    # 'MPC_TKO_SPEED':['MPC_Z_VEL_ALL','MPC_Z_VEL_MAX_UP'],
    # 'MPC_LAND_SPEED':['MPC_Z_VEL_ALL','MPC_Z_VEL_MAX_DN'],
    'MPC_TILTMAX_LND':'MPC_TILTMAX_AIR',
    # 'MPC_THR_HOVER':['MPC_THR_MAX','MPC_THR_MIN'],
    'MPC_THR_MAX':'MPC_THR_HOVER',
    'MPC_THR_MIN':'MPC_THR_HOVER'
}

config_rvfuzz ={
    'SYS_VEHICLE_RESP': [-0.4,(-1,1)],
    'MPC_ACC_HOR': [3, (1, 15)],
    'MPC_ACC_HOR_MAX': [5, (2, 15)],
    'MPC_TILTMAX_AIR': [45, (20, 89)],
    'MPC_ACC_DOWN_MAX': [3,(0.8,15)],
    'MPC_ACC_UP_MAX': [4,(1.0,15)],
    'MPC_JERK_MAX': [8,(2,50)],
    'MPC_JERK_AUTO': [4,(1,25)],
    'MPC_XY_VEL_ALL': [-10,(-20,20)],
    'MPC_XY_CRUISE': [5, (-1, 50)],
    'MPC_XY_VEL_MAX': [12,(0,10)],
    'MPC_Z_VEL_ALL': [-3,(-3,999)],
    'MPC_Z_V_AUTO_UP': [3,(-1,10)],
    'MPC_Z_VEL_MAX_UP': [3,(-1,10)],
    'MPC_Z_V_AUTO_DN': [1.5,(-1,10)],
    'MPC_Z_VEL_MAX_DN': [1.5,(-1,999)],
    'MPC_TKO_SPEED': [1.5,(0,999)],
    'MPC_LAND_SPEED': [0.7,(0,999)],
    'MPC_TILTMAX_LND': [12,(0,999)],
    'MPC_THR_HOVER':[0.5,(0,1)],
    'MPC_THR_MAX': [1, (-1, 20)],
    'MPC_THR_MIN': [0.12, (-1, 20)],
    'MC_PITCHRATE_MAX': [220, (0, 9999)],
    'MIS_YAW_ERR': [12,(0,999)],
    'MPC_YAWRAUTO_MAX': [45,(-1,999)]
}