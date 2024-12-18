// pch.cpp: 与预编译标头对应的源文件

#include "pch.h"

// 当使用预编译的头时，需要使用此源文件，编译才能成功。

#include "PX4Checker.h"
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <fstream>
#include <string>

using namespace std;

std::ofstream outfile;   ///zhou 

Command ReadCommand(int idx)
{
	unsigned int currentWP, coordFrame, type;
	double param1, param2, param3, param4, param5, param6, param7;
	unsigned int autoContinue;
	cin >> currentWP >> coordFrame >> type >> param1 >> param2 >> param3 >> param4 >> param5 >> param6 >> param7 >> autoContinue;
	Command currentCommand(idx, currentWP, coordFrame, (CommandType)type, param1, param2, param3, param4, param5, param6, param7, autoContinue);
	return currentCommand;
}
/// <summary>
///  zhou
/// </summary>
/// <param name="idx"></param>
/// <returns></returns>
Command ReadCommands(int idx, const std::vector<double>& otherValues)
{
	//unsigned int currentWP, coordFrame, type;
	//double param1, param2, param3, param4, param5, param6, param7;
	//unsigned int autoContinue;
	//cin >> currentWP >> coordFrame >> type >> param1 >> param2 >> param3 >> param4 >> param5 >> param6 >> param7 >> autoContinue;

	unsigned int currentWP = static_cast<unsigned int>(otherValues[0]);
	unsigned int coordFrame = static_cast<unsigned int>(otherValues[1]);
	unsigned int type = static_cast<unsigned int>(otherValues[2]);

	double param1 = otherValues[3];
	double param2 = otherValues[4];
	double param3 = otherValues[5];
	double param4 = otherValues[6];
	double param5 = otherValues[7];
	double param6 = otherValues[8];
	double param7 = otherValues[9];

	unsigned int autoContinue = static_cast<unsigned int>(otherValues[10]);

	Command currentCommand(idx, currentWP, coordFrame, (CommandType)type, param1, param2, param3, param4, param5, param6, param7, autoContinue);
	return currentCommand;
}

ParamSetCommand ReadParamSetCommand()
{
	std::string paramId;
	double value;
	cin >> paramId >> value;
	ParamSetCommand currentCommand(paramId, value);
	return currentCommand;
}

/// <summary>
/// read file into vector pointer
/// </summary>
/// <param name="filename"></param>
/// <param name="count"></param>
/// <returns></returns>
const char** readFileToVector(const char* filename, size_t* count) {
	static std::vector<std::string> lines;
	lines.clear(); // 清空之前的内容

	std::ifstream file(filename);

	if (!file.is_open()) {
		std::cerr << "Error opening file: " << filename << std::endl;
		*count = 0;
		return nullptr; // 文件打开失败，返回空指针
	}

	std::string line;
	while (std::getline(file, line)) {
		lines.push_back(line);
	}

	file.close();

	// 分配 C 风格的字符串数组
	const char** c_lines = new const char* [lines.size()];
	for (size_t i = 0; i < lines.size(); ++i) {
		c_lines[i] = lines[i].c_str();
	}

	*count = lines.size();
	return c_lines;
}

//int init(const std::vector<double>& newValues, const int commandNum, const std::vector<std::vector<double>>& commands)
//{
void init(double* newValues, size_t newValuesSize, int commandNum, double** commands, size_t* commandsSizes, size_t commandsCount)
{

	outfile.open("output.txt", std::ios::out | std::ios::trunc);   ///zhou

	// 将 newValues 转换为 std::vector
	std::vector<double> newValuesVec(newValues, newValues + newValuesSize);

	// 将 commands 转换为 std::vector<std::vector<double>>
	std::vector<std::vector<double>> commandsVec;
	for (size_t i = 0; i < commandsCount; ++i) {
		std::vector<double> command(commands[i], commands[i] + commandsSizes[i]);
		commandsVec.push_back(command);
	}

	PX4Checker* px4Checker = new PX4Checker();
	//// 先更改配置参数
	//cout << "input params" << endl;
	px4Checker->updateParameterWithParam(newValuesVec);
	//cout << "update finish" << endl;

	//cout << commandNum << endl;
	bool ret = false;
	ret = px4Checker->OnParamChanged();
	if (!ret)
	{
		delete px4Checker;
		px4Checker = nullptr;
//		return 0;
	}

	srand(time(nullptr));


	for (int i = 0; i < commandNum; ++i) {

		std::vector<double> command = commandsVec[i];
		double index = command[0];
		std::vector<double> otherValues(command.begin() + 1, command.end());

		/*
		for (double value : command) {
			std::cout << value << " ";
		}
		std::cout << std::endl;
		*/

		if (index >= 0)
		{
			Command currentCommand = ReadCommands(index, otherValues);
			ret = px4Checker->OnNewCommand(currentCommand);
		}
		// 规定: index == -1即为标志无人机当前状态的命令. 这在确定无人机初始位置和中途修改任务时极为有用.
		else if (index == -1)
		{
			Command currentCommand = ReadCommands(0, otherValues);
			ret = px4Checker->OnNewCommand(currentCommand, true);
		}
		// 规定: index == -2即为PARAM_SET.   ///no need 
		else if (index == -2)
		{
			ParamSetCommand currentCommand = ReadParamSetCommand();
			ret = px4Checker->UpdateParameter(Parameter(currentCommand.ParamId, currentCommand.Value));
		}
		if (!ret) break;
	}

	delete px4Checker;
	px4Checker = nullptr;

	outfile.close();
}
