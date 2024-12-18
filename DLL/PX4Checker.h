#pragma once

#include "Checker.h"

using namespace std;

extern std::ofstream outfile;

class PX4Checker : public Checker
{
public:
	PX4Checker();
	virtual bool UpdateParameter(const Parameter& newParam);
	virtual void updateParameters();    /// zhou
	virtual void updateParameterWithParam(const std::vector<double>& newValues);   ///zhou
	virtual bool OnParamChanged();
	virtual bool OnNewCommand(const Command& command, bool isPositionHint = false);
	unordered_map<string, Parameter> GetParams();
	vector<string> GetParamNames();
private:
	// Extracted mathematical functions.
	template<typename T>
	const T lerp(const T& a, const T& b, const T& s);
	template<typename T>
	constexpr T radians(T degrees);
	float get_distance_to_next_waypoint(double lat_now, double lon_now, double lat_next, double lon_next);
	double Distance(double x1, double y1, double x2, double y2);
	template<typename T>
	const T interpolate(const T& value, const T& x_low, const T& x_high, const T& y_low, const T& y_high);
	float computeT1(float a0, float v3, float j_max, float a_max);
	float computeT2(float T1, float T3, float a0, float v3, float j_max);
	// Customized helpers.
	bool DoubleEqual(double num1, double num2);
	void OverrideParamWithNotification(Parameter& param, double val);
	// PX4 parameters.
	unordered_map<string, Parameter> _params;
	vector<string> _paramNames;
};
#pragma once
