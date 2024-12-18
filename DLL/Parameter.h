#pragma once

#include <string>

class Parameter
{
public:
	Parameter();
	Parameter(const char* name, double value);
	Parameter(const std::string& name, double value);
	const std::string GetName() const;
	double GetValue() const;
	void SetValue(double val);
private:
	std::string _name;
	double _value;
};
#pragma once
