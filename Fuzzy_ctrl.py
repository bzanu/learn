import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# 1. 定义模糊变量
temp_error = ctrl.Antecedent(np.arange(-5, 6, 1), 'temp_error')
power = ctrl.Consequent(np.arange(0, 101, 1), 'power')

# 2. 定义隶属函数（三角形/梯形）
temp_error['NB'] = fuzz.trimf(temp_error.universe, [-5, -5, -2.5])
temp_error['NS'] = fuzz.trimf(temp_error.universe, [-5, -2.5, 0])
temp_error['ZE'] = fuzz.trimf(temp_error.universe, [-2.5, 0, 2.5])
temp_error['PS'] = fuzz.trimf(temp_error.universe, [0, 2.5, 5])
temp_error['PB'] = fuzz.trimf(temp_error.universe, [2.5, 5, 5])

power['S'] = fuzz.trimf(power.universe, [0, 0, 50])
power['M'] = fuzz.trimf(power.universe, [0, 50, 100])
power['B'] = fuzz.trimf(power.universe, [50, 100, 100])

# 3. 定义规则
rule1 = ctrl.Rule(temp_error['NB'], power['B'])
rule2 = ctrl.Rule(temp_error['NS'], power['B'])
rule3 = ctrl.Rule(temp_error['ZE'], power['M'])
rule4 = ctrl.Rule(temp_error['PS'], power['S'])
rule5 = ctrl.Rule(temp_error['PB'], power['S'])

# 4. 创建控制系统
ac_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])
ac_simulation = ctrl.ControlSystemSimulation(ac_ctrl)

# 5. 输入并计算
ac_simulation.input['temp_error'] = 5  # 当前28°C，目标26°C
ac_simulation.compute()

print(f"当前误差2°C，建议功率: {ac_simulation.output['power']:.1f}%")
# 输出约 65-70%
# 实际运行情况应该是下面这样，循环迭代运行
# import time

# target_temp = 26  # 目标温度

# while True:
#     # 1. 读取传感器（模拟）
#     current_temp = read_sensor()  # 比如 28°C
    
#     # 2. 计算误差
#     error = current_temp - target_temp  # 28 - 26 = 2
    
#     # 3. 送入模糊控制器
#     ac_simulation.input['temp_error'] = error
#     ac_simulation.compute()
#     power = ac_simulation.output['power']
    
#     # 4. 执行控制（调节加热器/制冷器功率）
#     set_heater_power(power)  # 或 set_cooler_power(power)
    
#     # 5. 等待下一个周期
#     time.sleep(1)  # 每秒采样一次