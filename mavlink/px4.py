import math

from pymavlink import mavutil
from pymavlink import mavwp
from paramDefualt import *
import time
from main import *
import os
import sys





def cmd_set_home(master,home_location,altitude):
    print("-----set home---",master.target_system," ", master.target_component,"-----------------------------")
    master.mav.command_long_send(master.target_system,master.target_component,
                                 mavutil.mavlink.MAV_CMD_DO_SET_HOME,1,
                                 0,0,0,0,
                                 home_location[0],home_location[1],altitude)

def handle_mission_current(msg,nextWaypoint):
    if msg.seq > nextWaypoint:
        print("moving to waypoint {0}".format(msg.seq))
        nextWaypoint = msg.seq+1
        print("next waypoint {0}".format(nextWaypoint))
    return nextWaypoint


def handle_global_positon_int(msg):
    return

def get_param(master,param_name):
    master.param_fetch_one(param_name)
    while True:
        try:
            msg = master.recv_match(type=['PARAM_VALUE', 'PARM'], blocking=True)
            # print(msg)
            # print(param_name)
            if msg.param_id == param_name:
                print("param name: {0}, param value: {1}".format(msg.param_id, msg.param_value))
                break
        except TimeoutError:
            print("failed to fetch param {0}".format(param_name))

def set_param(master,param_name,param_value):
    master.param_set_send(param_name, param_value)
    print("set param {0} done.".format(param_name,param_value))

    master.param_fetch_all()
    msg = master.recv_match(type=['PARAM_VALUE', 'PARM'], blocking=True)
    # print(msg)
    get_param(master,param_name)


def get_all_param(master):
    master.param_fetch_all()
    while True:
        try:
            msg = master.recv_match(type=['PARAM_VALUE', 'PARM'], blocking=True)
            print("param name: {0}, param value: {1}".format(msg.param_id, msg.param_value))
        except TimeoutError:
            print("failed to fetch param list")


def upload_default_config():
    print("start connecting....")
    master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
    master.wait_heartbeat(timeout=30)
    print("MAVLink connection established!")
    print("Heartbeat from system (system %u component %u)" % (
        master.target_system, master.target_component))

    for param in configuration_default.items():
        param_name = param[0]
        param_value = param[1]
        set_param(master, param_name, param_value)

    print("upload default config over")

def px4_conect(param_dict,waypoints):
    # cat PX4_HOME.sh
    # source PX4_HOME.sh
    # make posix_sitl_default jmavsim -j 4
    struck_flag = False

    print("start connecting....")
    master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
    master.wait_heartbeat(timeout=30)
    print("MAVLink connection established!")
    print("Heartbeat from system (system %u component %u)" % (
        master.target_system, master.target_component))

    for param in param_dict.items():
        param_name = param[0]
        param_value = param[1]
        set_param(master, param_name, param_value)

    print("set param done")
    # set home
    home_location = waypoints[0]
    cmd_set_home(master, home_location, 0)
    msg = master.recv_match(type=['COMMAND_ACK'], blocking=True)
    print(msg)
    print("set home:{0} {1}".format(home_location[0], home_location[1]))

    wp = mavwp.MAVWPLoader()

    for waypoint in enumerate(waypoints):
        seq = waypoint[0]
        lat = waypoint[1][0]
        lon = waypoint[1][1]
        alt = waypoint[1][2]
        autocontinue = 1
        current = 0
        param1 = 15.0
        frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT
        if seq == 0:
            current = 1
            p = mavutil.mavlink.MAVLink_mission_item_message(master.target_system, master.target_component, seq, frame,
                                                             mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                                                             current, autocontinue, param1, 0, 0, 0, lat, lon, alt)
        elif seq == len(waypoints) - 1:
            p = mavutil.mavlink.MAVLink_mission_item_message(master.target_system, master.target_component, seq, frame,
                                                             mavutil.mavlink.MAV_CMD_NAV_LAND,
                                                             current, autocontinue, 0, 0, 0, 0, lat, lon, alt)
        else:
            p = mavutil.mavlink.MAVLink_mission_item_message(master.target_system, master.target_component, seq, frame,
                                                             mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                                                             current, autocontinue, 0, 0, 0, 0, lat, lon, alt)
        wp.add(p)



    time.sleep(1)

    # send mission
    master.waypoint_clear_all_send()
    master.waypoint_count_send(wp.count())

    for i in range(wp.count()):
        msg = master.recv_match(type=['MISSION_REQUEST'], blocking=True)
        print(msg)
        master.mav.send(wp.wp(msg.seq))
        print('Sending waypoint {0}'.format(msg.seq))

    print("------------waypoint send over----------------------")

    # mission start
    while True:
        master.mav.command_long_send(1, 1, mavutil.mavlink.MAV_CMD_MISSION_START,
                                 0, 0, 0, 0, 0, 0, 0, 0)
        msg = master.recv_match(type=['COMMAND_ACK'], blocking=True)
        print("mission starting...")
        print(msg)
        if msg.result==0:
            print("mission start")
            break
        elif msg.result==1:
            time.sleep(2)
            continue
        elif msg.result==2:
            print("mission start failed")
            #master.mav.command_long_send(master.target_system, master.target_component,
                                         #mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN, 0, 2, 2, 2, 0, 0, 0, 0)
            return struck_flag

    status_pre = -1
    while True:
        # 接收当前任务状态
        msg = master.recv_match(type=['MISSION_CURRENT'], blocking=True)
        # speed 0
        if status_pre == msg.seq:
            start_time = time.time()
            while True:
                msg_p = master.recv_match(type=['LOCAL_POSITION_NED'], blocking=True)
                if abs(msg_p.vx)<0.5 and abs(msg_p.vy)<0.5 and abs(msg_p.vz)<0.5:
                    end_time = time.time()
                    if end_time-start_time>10:
                        print("strucking....")
                        struck_flag = True
                        # master.mav.command_long_send(master.target_system, master.target_component,mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN, 0, 2, 2, 2, 0, 0, 0, 0)
                        master.mav.command_long_send(master.target_system,master.target_component,mavutil.mavlink.MAV_CMD_NAV_LAND,0,0,0,0,0,home_location[0],home_location[1],0)
                        return struck_flag
                else:
                    break
        else:
            status_pre = msg.seq
            print("Flying to waypoint {0}".format(msg.seq))
        if msg.seq == msg.total - 1:
            while True:
                msg_pp = master.recv_match(type=['LOCAL_POSITION_NED'], blocking=True)
                if abs(msg_pp.z) < 0.5:
                    print("reach the destination")
                    break
            break
    return struck_flag


def start_mission(master):
    """Start the mission and monitor its status. Retry if failed."""
    retry_count = 5
    while retry_count > 0:
        try:
            master.mav.command_long_send(master.target_system, master.target_component,
                                         mavutil.mavlink.MAV_CMD_MISSION_START, 1, 0, 15, 0, 0, 0, 0, 0)
            msg = master.recv_match(type=['COMMAND_ACK'], blocking=True)
            print("Mission starting...")
            if msg.result == 0:
                print("Mission started")
                return True
            elif msg.result == 1:
                print("Retrying mission start...")
                time.sleep(2)
            elif msg.result == 2:
                print("Mission start failed")
                retry_count -= 1
                if retry_count > 0:
                    print(f"Retrying... {retry_count} retries left")
                    continue
                else:
                    print("Exceeded max retries. Mission failed.")
                    return False
        except Exception as e:
            print(f"Error starting mission: {e}")
            retry_count -= 1
            time.sleep(2)
            continue

    return False


def px4_one(param_name,param_value,waypoints):
    struck_flag = 0

    print("start connecting....")
    master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
    master.wait_heartbeat(timeout=30)
    print("MAVLink connection established!")
    print("Heartbeat from system (system %u component %u)" % (
        master.target_system, master.target_component))

    set_param(master, param_name, param_value)

    print("set param done")
    # set home
    home_location = waypoints[0]
    cmd_set_home(master, home_location, 0)
    msg = master.recv_match(type=['COMMAND_ACK'], blocking=True)
    print(msg)
    print("set home:{0} {1}".format(home_location[0], home_location[1]))

    wp = mavwp.MAVWPLoader()

    for waypoint in enumerate(waypoints):
        seq = waypoint[0]
        lat = waypoint[1][0]
        lon = waypoint[1][1]
        alt = waypoint[1][2]
        autocontinue = 1
        current = 0
        param1 = 15.0
        frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT
        if seq == 0:
            current = 1
            p = mavutil.mavlink.MAVLink_mission_item_message(master.target_system, master.target_component, seq, frame,
                                                             mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                                                             current, autocontinue, param1, 0, 0, 0, lat, lon, alt)
        elif seq == len(waypoints) - 1:
            p = mavutil.mavlink.MAVLink_mission_item_message(master.target_system, master.target_component, seq, frame,
                                                             mavutil.mavlink.MAV_CMD_NAV_LAND,
                                                             current, autocontinue, 0, 0, 0, 0, lat, lon, alt)
        else:
            p = mavutil.mavlink.MAVLink_mission_item_message(master.target_system, master.target_component, seq, frame,
                                                             mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                                                             current, autocontinue, 0, 0, 0, 0, lat, lon, alt)
        wp.add(p)

    time.sleep(1)

    # send mission
    master.waypoint_clear_all_send()
    master.waypoint_count_send(wp.count())

    for i in range(wp.count()):
        msg = master.recv_match(type=['MISSION_REQUEST'], blocking=True)
        print(msg)
        master.mav.send(wp.wp(msg.seq))
        print('Sending waypoint {0}'.format(msg.seq))

    print("------------waypoint send over----------------------")

    # mission start
    while True:
        master.mav.command_long_send(master.target_system, master.target_component, mavutil.mavlink.MAV_CMD_MISSION_START,
                                     1, 0, 15, 0, 0, 0, 0, 0)
        msg = master.recv_match(type=['COMMAND_ACK'], blocking=True)
        print("mission starting...")
        print(msg)
        # start_mission(master)
        if msg.result == 0:
            print("mission start")
            break
        elif msg.result == 1:
            time.sleep(2)
            continue
        elif msg.result == 2:
            print("mission start failed")
            # master.mav.command_long_send(master.target_system, master.target_component,
            # mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN, 0, 2, 2, 2, 0, 0, 0, 0)
            return struck_flag

    status_pre = -1
    while True:
        # 接收当前任务状态
        msg = master.recv_match(type=['MISSION_CURRENT'], blocking=True)
        # speed 0
        if status_pre == msg.seq:
            start_time = time.time()
            while True:
                msg_p = master.recv_match(type=['LOCAL_POSITION_NED'], blocking=True)
                if abs(msg_p.vx) < 0.5 and abs(msg_p.vy) < 0.5 and abs(msg_p.vz) < 0.5:
                    end_time = time.time()
                    if end_time - start_time > 300:
                        print("strucking....")
                        struck_flag = 1
                        # master.mav.command_long_send(master.target_system, master.target_component,mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN, 0, 2, 2, 2, 0, 0, 0, 0)
                        master.mav.command_long_send(master.target_system, master.target_component,
                                                     mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, home_location[0],
                                                     home_location[1], 0)
                        return struck_flag
                else:
                    break
        else:
            status_pre = msg.seq
            print("Flying to waypoint {0}".format(msg.seq))
        if msg.seq == msg.total - 1:
            while True:
                msg_pp = master.recv_match(type=['LOCAL_POSITION_NED'], blocking=True)
                if abs(msg_pp.z) < 0.5:
                    print("reach the destination")
                    break
            break
    return struck_flag




if __name__ == '__main__':
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
    # MPC_XY_VEL_ALL
    # MPC_XY_CRUISE
    # MPC_XY_VEL_MAX

    values = [100]
    scores = []
    for value in values:
        upload_default_config()
        print("---------------------starting {0} param mission ---------------------------".format(value))
        flag = px4_one("MPC_XY_VEL_ALL",value,mission_list)
        time.sleep(30)
        log_path = get_log()
        score1,score2,score3 = analyis_ulog(log_path)
        scores.append((value,score1,score2,flag))
        print(value,score1,score2,flag)



    for s in scores:
        print(s)

