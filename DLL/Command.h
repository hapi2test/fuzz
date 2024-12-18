#pragma once
#pragma once

#include <string>

enum CommandType
{
	MAV_CMD_NAV_WAYPOINT = 16,
	MAV_CMD_NAV_LOITER_UNLIM = 17,
	MAV_CMD_NAV_LOITER_TURNS = 18,
	MAV_CMD_NAV_LOITER_TIME = 19,
	MAV_CMD_NAV_RETURN_TO_LAUNCH = 20,
	MAV_CMD_NAV_LAND = 21,
	MAV_CMD_NAV_TAKEOFF = 22,
	MAV_CMD_NAV_LAND_LOCAL = 23,
	MAV_CMD_NAV_TAKEOFF_LOCAL = 24,
	MAV_CMD_NAV_FOLLOW = 25,
	MAV_CMD_NAV_CONTINUE_AND_CHANGE_ALT = 30,
	MAV_CMD_NAV_LOITER_TO_ALT = 31,
	MAV_CMD_DO_FOLLOW = 32,
	MAV_CMD_DO_FOLLOW_REPOSITION = 33,
	MAV_CMD_NAV_PATHPLANNING = 81,
	MAV_CMD_NAV_SPLINE_WAYPOINT = 82,
	MAV_CMD_NAV_VTOL_TAKEOFF = 84,
	MAV_CMD_NAV_VTOL_LAND = 85,
	MAV_CMD_NAV_DELAY = 93,
	MAV_CMD_NAV_PAYLOAD_PLACE = 95,
	MAV_CMD_CONDITION_DISTANCE = 114,
	MAV_CMD_CONDITION_YAW = 115,
	MAV_CMD_DO_SET_MODE = 176,
	MAV_CMD_DO_CHANGE_SPEED = 178,
	MAV_CMD_DO_SET_PARAMETER = 180,
	MAV_CMD_AIRFRAME_CONFIGURATION = 2520
};

struct Command {
	Command(unsigned int index, unsigned int currentWP, unsigned int coordFrame, CommandType type, double p1, double p2, double p3, double p4, double p5, double p6, double p7, unsigned int autoContinue);
	unsigned int Index;
	unsigned int CurrentWP;
	unsigned int CoordFrame;
	CommandType Type;
	double Param1;
	double Param2;
	double Param3;
	double Param4;
	double Param5;	// X / latitude.
	double Param6;	// Y / longitude.
	double Param7;	// Z / altitude.
	unsigned int AutoContinue;
};

struct ParamSetCommand {
	ParamSetCommand(std::string& id, double value);
	std::string ParamId;
	double Value;
};
