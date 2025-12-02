# 告诉 PX4 的构建系统：我要造一个新模块
px4_add_module(
	MODULE setpoint_fuzzer      # 模块名叫 setpoint_fuzzer
	MAIN setpoint_fuzzer        # 入口函数名
	STACK_MAIN 4000             # 给它分配的栈内存
	SRCS
		fuzzer_main.cpp     # 你的源码文件
	DEPENDS
		motion_planning     # <--- 核心！PositionSmoothing 就在这里面
		mathlib             # 数学库 (math::constrain 等)
)
