#pragma once
#pragma once

#include "Parameter.h"
#include "Command.h"
#include <string>
#include <unordered_map>
#include <vector>

class Checker
{
public:
	Checker();
	virtual bool UpdateParameter(const Parameter& newParam) = 0;
	virtual bool OnParamChanged() = 0;
	virtual bool OnNewCommand(const Command& command, bool isPositionHint = false) = 0;
protected:
	// Common UAV status.
	bool _inFlight = false;
	double _homeX = 0, _homeY = 0, _homeZ = 0;	// Home position.
	double _lastX = 0, _lastY = 0, _lastZ = 0, _lastYaw = 0;	// Position and yaw at last waypoint.
};
