#include "Parameter.h"

Parameter::Parameter() : _value(0) {}

Parameter::Parameter(const char* name, double value)
{
	_name = std::string(name);
	_value = value;
}

Parameter::Parameter(const std::string& name, double value)
{
	_name = name;
	_value = value;
}

const std::string Parameter::GetName() const
{
	return _name;
}

double Parameter::GetValue() const
{
	return _value;
}

void Parameter::SetValue(double val)
{
	_value = val;
}
