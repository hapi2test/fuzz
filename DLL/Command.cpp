#include "Command.h"

Command::Command(unsigned int index, unsigned int currentWP, unsigned int coordFrame, CommandType type, double p1, double p2, double p3, double p4, double p5, double p6, double p7, unsigned int autoContinue)
{
	Index = index;
	CurrentWP = currentWP;
	CoordFrame = coordFrame;
	Type = type;
	Param1 = p1;
	Param2 = p2;
	Param3 = p3;
	Param4 = p4;
	Param5 = p5;
	Param6 = p6;
	Param7 = p7;
	AutoContinue = autoContinue;
}

ParamSetCommand::ParamSetCommand(std::string& id, double value)
{
	ParamId = id;
	Value = value;
}
