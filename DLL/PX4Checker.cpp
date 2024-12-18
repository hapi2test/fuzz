#include "PX4Checker.h"
#include <algorithm>
#include <cmath>
#include <iostream>
#include <fstream>

using namespace std;



PX4Checker::PX4Checker()
{
	_lastYaw = 90;
	// Default values in documentation.
	_params["MIS_DIST_1WP"] = Parameter("MIS_DIST_1WP", 900.0);
	_params["MIS_DIST_WPS"] = Parameter("MIS_DIST_WPS", 900.0);
	_params["MIS_TAKEOFF_ALT"] = Parameter("MIS_TAKEOFF_ALT", 2.5);
	_params["MIS_YAW_ERR"] = Parameter("MIS_YAW_ERR", 12.0);
	_params["MIS_YAW_TMT"] = Parameter("MIS_YAW_TMT", -1.0);
	_params["NAV_FW_ALT_RAD"] = Parameter("NAV_FW_ALT_RAD", 10);
	_params["NAV_FW_ALTL_RAD"] = Parameter("NAV_FW_ALTL_RAD", 5);
	_params["NAV_MC_ALT_RAD"] = Parameter("NAV_MC_ALT_RAD", 0.8);
	_params["NAV_ACC_RAD"] = Parameter("NAV_ACC_RAD", 10);
	_params["MPC_YAWRAUTO_MAX"] = Parameter("MPC_YAWRAUTO_MAX", 45);
	_params["MPC_XY_CRUISE"] = Parameter("MPC_XY_CRUISE", 5);
	_params["MPC_ACC_DOWN_MAX"] = Parameter("MPC_ACC_DOWN_MAX", 3.0);
	_params["MPC_Z_V_AUTO_DN"] = Parameter("MPC_Z_V_AUTO_DN", 1.5);
	_params["MPC_ACC_UP_MAX"] = Parameter("MPC_ACC_UP_MAX", 4.0);
	_params["MPC_Z_V_AUTO_UP"] = Parameter("MPC_Z_V_AUTO_UP", 3.0);
	_params["MPC_TKO_SPEED"] = Parameter("MPC_TKO_SPEED", 1.5);
	_params["MPC_TKO_RAMP_T"] = Parameter("MPC_TKO_RAMP_T", 3.0);
	_params["MPC_JERK_AUTO"] = Parameter("MPC_JERK_AUTO", 4);
	_params["MPC_ACC_HOR"] = Parameter("MPC_ACC_HOR", 3);
	_params["MPC_LAND_ALT1"] = Parameter("MPC_LAND_ALT1", 10);
	_params["MPC_LAND_ALT2"] = Parameter("MPC_LAND_ALT2", 5);
	_params["MPC_LAND_ALT3"] = Parameter("MPC_LAND_ALT3", 1);
	_params["MPC_LAND_SPEED"] = Parameter("MPC_LAND_SPEED", 0.7);
	_params["MPC_Z_VEL_MAX_DN"] = Parameter("MPC_Z_VEL_MAX_DN", 1.5);
	_params["MPC_LAND_CRWL"] = Parameter("MPC_LAND_CRWL", 0.3);
	_params["MPC_YAW_MODE"] = Parameter("MPC_YAW_MODE", 4);
	_params["MC_PITCHRATE_MAX"] = Parameter("MC_PITCHRATE_MAX", 220);
	_params["MC_YAWRATE_MAX"] = Parameter("MC_YAWRATE_MAX", 200);
	_params["MC_YAW_WEIGHT"] = Parameter("MC_YAW_WEIGHT", 0.4);
	_params["SYS_VEHICLE_RESP"] = Parameter("SYS_VEHICLE_RESP", -0.4);
	_params["MPC_ACC_HOR_MAX"] = Parameter("MPC_ACC_HOR_MAX", 5.0);
	_params["MPC_TILTMAX_AIR"] = Parameter("MPC_TILTMAX_AIR", 45.0);
	_params["MPC_JERK_MAX"] = Parameter("MPC_JERK_MAX", 8.0);
	_params["MPC_XY_VEL_ALL"] = Parameter("MPC_XY_VEL_ALL", -10.0);
	_params["MPC_XY_VEL_MAX"] = Parameter("MPC_XY_VEL_MAX", 12.0);
	_params["MPC_Z_VEL_ALL"] = Parameter("MPC_Z_VEL_ALL", -3.0);
	_params["MPC_Z_VEL_MAX_UP"] = Parameter("MPC_Z_VEL_MAX_UP", 3.0);
	_params["MPC_TILTMAX_LND"] = Parameter("MPC_TILTMAX_LND", 12.0);
	_params["MPC_THR_HOVER"] = Parameter("MPC_THR_HOVER", 0.5);
	_params["MPC_THR_MAX"] = Parameter("MPC_THR_MAX ", 1.0);
	_params["MPC_THR_MIN"] = Parameter("MPC_THR_MIN ", 0.2);
	for (pair<const string, Parameter> param : _params)
	{
		_paramNames.push_back(param.first);
	}



}
/// <summary>
/// / zhou 
///  �����������ò�����ֵ
/// </summary>
void PX4Checker::updateParameters() {
	for (auto& param : _params) {
		double newValue;
		//std::cout << "Enter new value for " << param.first << ": ";
		std::cin >> newValue;
		param.second.SetValue(newValue);
	}
}
/// <summary>
/// with params to update
/// zhou
/// </summary>
/// <param name="newParam"></param>
/// <returns></returns>
void PX4Checker::updateParameterWithParam(const std::vector<double>& newValues) {
	int index = 0;
	for (auto& param : _params) {
		param.second.SetValue(newValues[index]);
		index++;
	}
}


bool PX4Checker::UpdateParameter(const Parameter& newParam)
{
	if (_params.count(newParam.GetName()) == 0) return false;
	_params[newParam.GetName()] = newParam;
	cout << "[*] Parameter " << newParam.GetName() << " has been set to " << newParam.GetValue() << endl;
	outfile << "[*] Parameter " << newParam.GetName() << " has been set to " << newParam.GetValue() << endl;   ////add
	return OnParamChanged();
}

bool PX4Checker::OnParamChanged()
{
	if (_params["SYS_VEHICLE_RESP"].GetValue() >= 0)
	{
		double responsiveness = _params["SYS_VEHICLE_RESP"].GetValue() * _params["SYS_VEHICLE_RESP"].GetValue();
		OverrideParamWithNotification(_params["MPC_ACC_HOR"], lerp(1.0, 15.0, responsiveness));
		OverrideParamWithNotification(_params["MPC_ACC_HOR_MAX"], lerp(2.0, 15.0, responsiveness));
		if (responsiveness < 0.5)
			OverrideParamWithNotification(_params["MPC_TILTMAX_AIR"], 45.0);
		else
			OverrideParamWithNotification(_params["MPC_TILTMAX_AIR"], fmin(89, lerp(45.0, 70.0, (responsiveness - 0.5) * 2.0)));
		OverrideParamWithNotification(_params["MPC_ACC_DOWN_MAX"], lerp(0.8, 15.0, responsiveness));
		OverrideParamWithNotification(_params["MPC_ACC_UP_MAX"], lerp(1.0, 15.0, responsiveness));
		OverrideParamWithNotification(_params["MPC_JERK_MAX"], lerp(2.0, 50.0, responsiveness));
		OverrideParamWithNotification(_params["MPC_JERK_AUTO"], lerp(1.0, 25.0, responsiveness));
	}
	if (_params["MPC_XY_VEL_ALL"].GetValue() >= 0)
	{
		OverrideParamWithNotification(_params["MPC_XY_CRUISE"], _params["MPC_XY_VEL_ALL"].GetValue());
		OverrideParamWithNotification(_params["MPC_XY_VEL_MAX"], _params["MPC_XY_VEL_ALL"].GetValue());
	}
	if (_params["MPC_Z_VEL_ALL"].GetValue() >= 0)
	{
		OverrideParamWithNotification(_params["MPC_Z_V_AUTO_UP"], _params["MPC_Z_VEL_ALL"].GetValue());
		OverrideParamWithNotification(_params["MPC_Z_VEL_MAX_UP"], _params["MPC_Z_VEL_ALL"].GetValue());
		OverrideParamWithNotification(_params["MPC_Z_V_AUTO_DN"], _params["MPC_Z_VEL_ALL"].GetValue() * 0.75);
		OverrideParamWithNotification(_params["MPC_Z_VEL_MAX_DN"], _params["MPC_Z_VEL_ALL"].GetValue() * 0.75);
		OverrideParamWithNotification(_params["MPC_TKO_SPEED"], _params["MPC_Z_VEL_ALL"].GetValue() * 0.6);
		OverrideParamWithNotification(_params["MPC_LAND_SPEED"], _params["MPC_Z_VEL_ALL"].GetValue() * 0.5);
	}
	if (_params["MPC_TILTMAX_AIR"].GetValue() > 89)
	{
		cout << "[!] Maximum tilt limit MPC_TILTMAX_AIR has been constrained to a safe value." << endl;
		outfile << "[!] Maximum tilt limit MPC_TILTMAX_AIR has been constrained to a safe value." << endl;   ////add
		_params["MPC_TILTMAX_AIR"].SetValue(89);
	}
	if (_params["MPC_TILTMAX_LND"].GetValue() > _params["MPC_TILTMAX_AIR"].GetValue())
	{
		cout << "[!] Land tilt limit MPC_TILTMAX_LND has been constrained by maximum tilt MPC_TILTMAX_AIR." << endl;

		outfile << "[!] Land tilt limit MPC_TILTMAX_LND has been constrained by maximum tilt MPC_TILTMAX_AIR." << endl;

		_params["MPC_TILTMAX_LND"].SetValue(_params["MPC_TILTMAX_AIR"].GetValue());
	}
	if (_params["MPC_XY_CRUISE"].GetValue() > _params["MPC_XY_VEL_MAX"].GetValue())
	{
		cout << "[!] Cruise speed MPC_XY_CRUISE has been constrained by maximum speed MPC_XY_VEL_MAX." << endl;

		outfile << "[!] Cruise speed MPC_XY_CRUISE has been constrained by maximum speed MPC_XY_VEL_MAX." << endl;
		_params["MPC_XY_CRUISE"].SetValue(_params["MPC_XY_VEL_MAX"].GetValue());
	}
	if (_params["MPC_Z_V_AUTO_UP"].GetValue() > _params["MPC_Z_VEL_MAX_UP"].GetValue())
	{
		cout << "[!] Ascent speed MPC_Z_V_AUTO_UP has been constrained by max speed MPC_Z_VEL_MAX_UP." << endl;

		outfile << "[!] Ascent speed MPC_Z_V_AUTO_UP has been constrained by max speed MPC_Z_VEL_MAX_UP." << endl;
		_params["MPC_Z_V_AUTO_UP"].SetValue(_params["MPC_Z_VEL_MAX_UP"].GetValue());
	}
	if (_params["MPC_Z_V_AUTO_DN"].GetValue() > _params["MPC_Z_VEL_MAX_DN"].GetValue())
	{
		cout << "[!] Descent speed MPC_Z_V_AUTO_DN has been constrained by max speed MPC_Z_VEL_MAX_DN." << endl;

		outfile << "[!] Descent speed MPC_Z_V_AUTO_DN has been constrained by max speed MPC_Z_VEL_MAX_DN." << endl;

		_params["MPC_Z_V_AUTO_DN"].SetValue(_params["MPC_Z_VEL_MAX_DN"].GetValue());
	}
	if (_params["MPC_THR_HOVER"].GetValue() > _params["MPC_THR_MAX"].GetValue() || _params["MPC_THR_HOVER"].GetValue() < _params["MPC_THR_MIN"].GetValue())
	{
		if (_params["MPC_THR_HOVER"].GetValue() > _params["MPC_THR_MAX"].GetValue()) _params["MPC_THR_HOVER"].SetValue(_params["MPC_THR_MAX"].GetValue());
		else _params["MPC_THR_HOVER"].SetValue(_params["MPC_THR_MIN"].GetValue());
		cout << "[!] Hover thrust MPC_THR_HOVER has been constrained by min/max thrust." << endl;

		outfile << "[!] Hover thrust MPC_THR_HOVER has been constrained by min/max thrust." << endl;
	}
	OverrideParamWithNotification(_params["MPC_TKO_SPEED"], fmin(_params["MPC_TKO_SPEED"].GetValue(), _params["MPC_Z_VEL_MAX_UP"].GetValue()));
	OverrideParamWithNotification(_params["MPC_LAND_SPEED"], fmin(_params["MPC_LAND_SPEED"].GetValue(), _params["MPC_Z_VEL_MAX_DN"].GetValue()));
	return true;
}

bool PX4Checker::OnNewCommand(const Command& command, bool isPositionHint)
{



	Command currentCommand = command;
	constexpr double ONE_METER = 0.00001;
	if (isPositionHint)
	{
		_lastX = currentCommand.Param5;
		_lastY = currentCommand.Param6;
		_lastZ = currentCommand.Param7;

		// 输出当前的坐标值  zhou
		cout << "[*] Position Hint - X: " << _lastX << ", Y: " << _lastY << ", Z: " << _lastZ << endl;
		outfile << "[*] Position Hint - X: " << _lastX << ", Y: " << _lastY << ", Z: " << _lastZ << endl;

		
		return true;
	}
	double totalTimeCost, newYaw, yawDiff, yawTime, pitchDiff, pitchTime, jMax, aMax, aMaxZUp, aMaxZDown, deltaVelocity, t1, t2, xyDistance, zDistance, landVerticalSpeed;
	switch (currentCommand.Type)
	{
	case MAV_CMD_NAV_TAKEOFF:
	case MAV_CMD_NAV_TAKEOFF_LOCAL:
	case MAV_CMD_NAV_VTOL_TAKEOFF:
		totalTimeCost = 0;
		_homeX = currentCommand.Param5;
		_homeY = currentCommand.Param6;
		_homeZ = currentCommand.Param7;

		// 输出家位置的坐标值  zhou
		cout << "[*] Home Position - X: " << _homeX << ", Y: " << _homeY << ", Z: " << _homeZ << endl;
		outfile << "[*] Home Position - X: " << _homeX << ", Y: " << _homeY << ", Z: " << _homeZ << endl;


		// Check if vehicle needs to takeoff.
		if (_inFlight)
		{
			if (currentCommand.Type == MAV_CMD_NAV_VTOL_TAKEOFF)
			{
				cout << "[*] Check: takeoff: " << _params["NAV_FW_ALT_RAD"].GetName() << " < " << _homeZ << " : " << (_params["NAV_FW_ALT_RAD"].GetValue() < _homeZ) << endl;

				outfile << "[*] Check: takeoff: " << _params["NAV_FW_ALT_RAD"].GetName() << " < " << _homeZ << " : " << (_params["NAV_FW_ALT_RAD"].GetValue() < _homeZ) << endl;
				cout << "[*] Check: takeoff: " << _params["NAV_FW_ALTL_RAD"].GetName() << " < " << _homeZ << " : " << (_params["NAV_FW_ALTL_RAD"].GetValue() < _homeZ) << endl;

				outfile << "[*] Check: takeoff: " << _params["NAV_FW_ALTL_RAD"].GetName() << " < " << _homeZ << " : " << (_params["NAV_FW_ALTL_RAD"].GetValue() < _homeZ) << endl;
			}
			else
			{
				cout << "[*] Check: takeoff: " << _params["NAV_MC_ALT_RAD"].GetName() << " < " << _homeZ << " : " << (_params["NAV_MC_ALT_RAD"].GetValue() < _homeZ) << endl;

				outfile << "[*] Check: takeoff: " << _params["NAV_MC_ALT_RAD"].GetName() << " < " << _homeZ << " : " << (_params["NAV_MC_ALT_RAD"].GetValue() < _homeZ) << endl;
			}
			if (_params["MIS_TAKEOFF_ALT"].GetValue() + _lastZ > _homeZ)
			{
				cout << "[!] Takeoff altitude is lower than MIS_TAKEOFF_ALT. Overriding the former." << endl;

				outfile << "[!] Takeoff altitude is lower than MIS_TAKEOFF_ALT. Overriding the former." << endl;
				_homeZ = fmaxf(_homeZ, _params["MIS_TAKEOFF_ALT"].GetValue() + _lastZ);
			}
			_inFlight = true;
		}
		// Check if vehicle is too far away from takeoff site.
		if (_params["MIS_DIST_1WP"].GetValue() > 0)
		{
			float distToFirstWP = get_distance_to_next_waypoint(_lastX, _lastY, currentCommand.Param5, currentCommand.Param6);
			if (distToFirstWP >= _params["MIS_DIST_1WP"].GetValue())
			{
				cout << "[!] First waypoint too far away! Check MIS_DIST_1WP." << endl;

				outfile << "[!] First waypoint too far away! Check MIS_DIST_1WP." << endl;
				return false;
			}
		}
		if (_params["MIS_DIST_WPS"].GetValue() > 0)
		{
			float distToFirstWP = get_distance_to_next_waypoint(_lastX, _lastY, currentCommand.Param5, currentCommand.Param6);
			if (distToFirstWP > _params["MIS_DIST_WPS"].GetValue())
			{
				cout << "[!] First waypoint too far away! Check MIS_DIST_WPS." << endl;

				outfile << "[!] First waypoint too far away! Check MIS_DIST_WPS." << endl;
				return false;
			}
		}
		cout << "[*] Check: takeoff: " << _params["NAV_ACC_RAD"].GetName() << " >= " << Distance(_lastX, _lastY, _homeX, _homeY) << " : " << (_params["NAV_ACC_RAD"].GetValue() >= Distance(_lastX, _lastY, _homeX, _homeY)) << endl;

		outfile << "[*] Check: takeoff: " << _params["NAV_ACC_RAD"].GetName() << " >= " << Distance(_lastX, _lastY, _homeX, _homeY) << " : " << (_params["NAV_ACC_RAD"].GetValue() >= Distance(_lastX, _lastY, _homeX, _homeY)) << endl;
		jMax = _params["MPC_JERK_AUTO"].GetValue();
		aMaxZUp = fmin(_params["MPC_ACC_UP_MAX"].GetValue(), _params["MPC_TKO_SPEED"].GetValue() / _params["MPC_TKO_RAMP_T"].GetValue());
		deltaVelocity = _params["MPC_TKO_SPEED"].GetValue();
		t1 = computeT1(0, deltaVelocity, jMax, aMaxZUp);
		t2 = computeT2(t1, t1, 0, deltaVelocity, jMax);
		totalTimeCost += 2 * t1 + t2;
		if (DoubleEqual(_params["MPC_TKO_SPEED"].GetValue(), 0))
		{
			cout << "[!] Devided by zero! Please check MPC_TKO_SPEED!" << endl;

			outfile << "[!] Devided by zero! Please check MPC_TKO_SPEED!" << endl;
			return false;
		}
		totalTimeCost += _homeZ / _params["MPC_TKO_SPEED"].GetValue();
		cout << "[*] Estimated take off time: " << totalTimeCost << endl;

		outfile << "[*] Estimated take off time: " << totalTimeCost << endl;
		_lastX = _homeX;
		_lastY = _homeY;
		_lastZ = _homeZ;
		break;
	case MAV_CMD_NAV_RETURN_TO_LAUNCH:
		currentCommand.Param5 = _homeX;
		currentCommand.Param6 = _homeY;
		currentCommand.Param7 = _homeZ;
	case MAV_CMD_NAV_WAYPOINT:
		totalTimeCost = 0;
		newYaw = currentCommand.Param4 == 0 ? abs(atan2(currentCommand.Param6 - _lastY, currentCommand.Param5 - _lastX) * 180 / 3.1415926) : currentCommand.Param4;
		yawDiff = min(abs(newYaw - _lastYaw), _lastYaw + 360 - newYaw);
		if (_params["MIS_YAW_ERR"].GetValue() > yawDiff)
		{
			cout << "[*] A yaw alignment is skipped because is under MIS_YAW_ERR. Double check is recommended" << endl;

			outfile << "[*] A yaw alignment is skipped because is under MIS_YAW_ERR. Double check is recommended" << endl;
		}
		yawDiff = fmaxl(yawDiff - _params["MIS_YAW_ERR"].GetValue(), 0);
		// yawTime = yawDiff / min(MPC_YAWRAUTO_MAX.GetValue(), MC_YAWRATE_MAX.GetValue());		// Issue #20858.
		yawTime = yawDiff / _params["MPC_YAWRAUTO_MAX"].GetValue();
		if (_params["MIS_YAW_TMT"].GetValue() >= 1.192092896e-07F && yawTime >= _params["MIS_YAW_TMT"].GetValue())
		{
			cout << "[!] Yaw alignment time is beyond MIS_YAW_TMT. This mission is considered failed." << endl;

			outfile << "[!] Yaw alignment time is beyond MIS_YAW_TMT. This mission is considered failed." << endl;
			return false;
		}
		cout << "[*] Yaw alignment time: " << yawTime << std::endl;

		outfile << "[*] Yaw alignment time: " << yawTime << std::endl;
		jMax = _params["MPC_JERK_AUTO"].GetValue();
		aMax = _params["MPC_ACC_HOR"].GetValue();
		deltaVelocity = _params["MPC_XY_CRUISE"].GetValue();
		t1 = computeT1(0, deltaVelocity, jMax, aMax);
		t2 = computeT2(t1, t1, 0, deltaVelocity, jMax);
		totalTimeCost += 2 * t1 + t2;
		xyDistance = Distance(_lastX, _lastY, currentCommand.Param5, currentCommand.Param6) / ONE_METER;
		xyDistance -= 2 * _params["NAV_ACC_RAD"].GetValue();
		if (DoubleEqual(_params["MPC_XY_CRUISE"].GetValue(), 0))
		{
			cout << "[!] Devided by zero! Please check MPC_XY_CRUISE!" << endl;

			outfile << "[!] Devided by zero! Please check MPC_XY_CRUISE!" << endl;
			return false;
		}
		if (xyDistance < 0) {
			std::cout << "[!] NAV_ACC_RAD is too high! Some fly-to cruises are ignored!" << endl;

			outfile << "[!] NAV_ACC_RAD is too high! Some fly-to cruises are ignored!" << endl;
		}
		else
			totalTimeCost += xyDistance / _params["MPC_XY_CRUISE"].GetValue();
		zDistance = currentCommand.Param7 - _lastZ;
		if (zDistance > 0)
		{
			aMaxZUp = _params["MPC_ACC_UP_MAX"].GetValue();
			deltaVelocity = _params["MPC_Z_V_AUTO_UP"].GetValue();
			t1 = computeT1(0, deltaVelocity, jMax, aMaxZUp);
			t2 = computeT2(t1, t1, 0, deltaVelocity, jMax);
			if (2 * t1 + t2 > totalTimeCost)
			{
				cout << "[!] Climb rate is too slow! The drone cannot reach its desired altitude before it reaches a waypoint!" << endl;

				outfile << "[!] Climb rate is too slow! The drone cannot reach its desired altitude before it reaches a waypoint!" << endl;
				totalTimeCost = fmax(totalTimeCost, 2 * t1 + t2);
			}
			zDistance -= 2 * _params["NAV_ACC_RAD"].GetValue();
			if (DoubleEqual(_params["MPC_Z_V_AUTO_UP"].GetValue(), 0))
			{
				cout << "[!] Devided by zero! Please check MPC_Z_V_AUTO_UP!" << endl;

				outfile << "[!] Devided by zero! Please check MPC_Z_V_AUTO_UP!" << endl;
				return false;
			}
			totalTimeCost = fmax(zDistance / _params["MPC_Z_V_AUTO_UP"].GetValue(), totalTimeCost);
		}
		else
		{
			aMaxZDown = _params["MPC_ACC_DOWN_MAX"].GetValue();
			deltaVelocity = _params["MPC_Z_V_AUTO_DN"].GetValue();
			t1 = computeT1(0, deltaVelocity, jMax, aMaxZDown);
			t2 = computeT2(t1, t1, 0, deltaVelocity, jMax);
			if (2 * t1 + t2 > totalTimeCost)
			{
				cout << "[!] Descend rate is too slow! The drone cannot reach its desired altitude before it reaches a waypoint!" << endl;

				outfile << "[!] Descend rate is too slow! The drone cannot reach its desired altitude before it reaches a waypoint!" << endl;
				totalTimeCost = fmax(totalTimeCost, 2 * t1 + t2);
			}
			zDistance -= 2 * _params["NAV_ACC_RAD"].GetValue();
			if (DoubleEqual(_params["MPC_Z_V_AUTO_DN"].GetValue(), 0))
			{
				cout << "[!] Devided by zero! Please check MPC_Z_V_AUTO_DN!" << endl;

				outfile << "[!] Devided by zero! Please check MPC_Z_V_AUTO_DN!" << endl;
				return false;
			}
			totalTimeCost = fmax(zDistance / _params["MPC_Z_V_AUTO_DN"].GetValue(), totalTimeCost);
		}
		pitchDiff = atan2(zDistance, abs(Distance(_lastX, _lastY, currentCommand.Param5, currentCommand.Param6) / ONE_METER)) * 180 / 3.1415926;
		pitchTime = pitchDiff / _params["MC_PITCHRATE_MAX"].GetValue();
		if (pitchTime > totalTimeCost)
		{
			cout << "[!] Pitch rate is too slow! The drone cannot reach its desired altitude before it reaches a waypoint!" << endl;

			outfile << "[!] Pitch rate is too slow! The drone cannot reach its desired altitude before it reaches a waypoint!" << endl;
			totalTimeCost = max(pitchTime, totalTimeCost);
		}
		if (DoubleEqual(_params["MPC_YAW_MODE"].GetValue(), 4))
		{
			totalTimeCost += yawTime;
		}
		else
		{
			if (yawTime > totalTimeCost)
			{
				cout << "[!] Yaw rate is too slow! The drone cannot align its yaw before it reaches a waypoint!" << endl;

				outfile << "[!] Yaw rate is too slow! The drone cannot align its yaw before it reaches a waypoint!" << endl;
			}
			totalTimeCost = max(yawTime, totalTimeCost);
		}
		cout << "[*] Estimated time cost: " << totalTimeCost << endl;

		outfile << "[*] Estimated time cost: " << totalTimeCost << endl;
		_lastX = currentCommand.Param5;
		_lastY = currentCommand.Param6;
		_lastZ = currentCommand.Param7;


		// 输出最后的坐标值  zhou
		cout << "[*] Last Position - X: " << _lastX << ", Y: " << _lastY << ", Z: " << _lastZ << endl;
		outfile << "[*] Last Position - X: " << _lastX << ", Y: " << _lastY << ", Z: " << _lastZ << endl;

		_lastYaw = newYaw;
		break;
	case MAV_CMD_NAV_LAND:
	case MAV_CMD_NAV_VTOL_LAND:
		if (_lastZ <= _params["MPC_LAND_ALT3"].GetValue())
			landVerticalSpeed = _params["MPC_LAND_CRWL"].GetValue();
		else landVerticalSpeed = interpolate(_lastZ, _params["MPC_LAND_ALT2"].GetValue(), _params["MPC_LAND_ALT1"].GetValue(), _params["MPC_LAND_SPEED"].GetValue(), _params["MPC_Z_VEL_MAX_DN"].GetValue());
		cout << "[*] Estimated average landing speed: " << landVerticalSpeed << endl;

		outfile << "[*] Estimated average landing speed: " << landVerticalSpeed << endl;
		_inFlight = false;
		_lastX = currentCommand.Param5;
		_lastY = currentCommand.Param6;
		_lastZ = currentCommand.Param7;

		// 输出最后的坐标值  zhou
		cout << "[*] Last Position - X: " << _lastX << ", Y: " << _lastY << ", Z: " << _lastZ << endl;
		outfile << "[*] Last Position - X: " << _lastX << ", Y: " << _lastY << ", Z: " << _lastZ << endl;

		_lastYaw = 90;
		break;
	case MAV_CMD_AIRFRAME_CONFIGURATION:
		// CHECK: Keep gear up in air.
		if (currentCommand.Param2 == 0 && _lastZ > 2.0) {
			std::cout << "[!] Landing gear down in air. This is a very dangerous behavior." << std::endl;

			outfile << "[!] Landing gear down in air. This is a very dangerous behavior." << std::endl;
		}
		break;
	default:
		break;
	}
	return true;
}

unordered_map<string, Parameter> PX4Checker::GetParams()
{
	return _params;
}

vector<string> PX4Checker::GetParamNames()
{
	return _paramNames;
}

template<typename T>
inline const T PX4Checker::lerp(const T& a, const T& b, const T& s)
{
	return (static_cast<T>(1) - s) * a + s * b;
}

template<typename T>
constexpr T PX4Checker::radians(T degrees)
{
	return degrees * (static_cast<T>(3.141592653589793238462643383280) / static_cast<T>(180));
}

template<typename T>
const T PX4Checker::interpolate(const T& value, const T& x_low, const T& x_high, const T& y_low, const T& y_high)
{
	if (value <= x_low) {
		return y_low;

	}
	else if (value > x_high) {
		return y_high;

	}
	else {
		T a = (y_high - y_low) / (x_high - x_low);
		T b = y_low - (a * x_low);
		return (a * value) + b;
	}
}

float PX4Checker::get_distance_to_next_waypoint(double lat_now, double lon_now, double lat_next, double lon_next)
{
	const double lat_now_rad = radians(lat_now);
	const double lat_next_rad = radians(lat_next);

	const double d_lat = lat_next_rad - lat_now_rad;
	const double d_lon = radians(lon_next) - radians(lon_now);

	const double a = sin(d_lat / 2.0) * sin(d_lat / 2.0) + sin(d_lon / 2.0) * sin(d_lon / 2.0) * cos(lat_now_rad) * cos(
		lat_next_rad);

	const double c = atan2(sqrt(a), sqrt(1.0 - a));

	return static_cast<float>(6371000 * 2.0 * c);
}

double PX4Checker::Distance(double x1, double y1, double x2, double y2)
{
	double diffX = x1 - x2;
	double diffY = y1 - y2;
	return sqrt(diffX * diffX + diffY * diffY);
}

float PX4Checker::computeT1(float a0, float v3, float j_max, float a_max)
{
	float delta = 2.f * a0 * a0 + 4.f * j_max * v3;

	if (delta < 0.f) {
		return 0.f;
	}

	float sqrt_delta = sqrtf(delta);
	float T1_plus = (-a0 + 0.5f * sqrt_delta) / j_max;
	float T1_minus = (-a0 - 0.5f * sqrt_delta) / j_max;

	float T3_plus = a0 / j_max + T1_plus;
	float T3_minus = a0 / j_max + T1_minus;

	float T1 = 0.f;

	if (T1_plus >= 0.f && T3_plus >= 0.f) {
		T1 = T1_plus;

	}
	else if (T1_minus >= 0.f && T3_minus >= 0.f) {
		T1 = T1_minus;
	}

	return std::max(T1, 0.f);
}

float PX4Checker::computeT2(float T1, float T3, float a0, float v3, float j_max)
{
	float T2 = 0.f;

	float den = a0 + j_max * T1;

	if (std::abs(den) > FLT_EPSILON) {
		T2 = (-0.5f * T1 * T1 * j_max - T1 * T3 * j_max - T1 * a0 + 0.5f * T3 * T3 * j_max - T3 * a0 + v3) / den;
	}

	return std::max(T2, 0.f);
}

bool PX4Checker::DoubleEqual(double num1, double num2)
{
	double diff = num1 - num2;
	if (diff > -0.000001 && diff < 0.000001)
		return true;
	return false;
}

void PX4Checker::OverrideParamWithNotification(Parameter& param, double val)
{
	if (DoubleEqual(param.GetValue(), val)) return;
	param.SetValue(val);
	cout << "[*] Parameter: " << param.GetName() << " is set to " << val << " due to an override." << endl;

	outfile << "[*] Parameter: " << param.GetName() << " is set to " << val << " due to an override." << endl;
	_params[param.GetName()] = param;
}
