import math

def calculate_los_heading(current_x, current_y, target_x, target_y, lookahead_dist):
    """
    核心LOS算法逻辑
    """
    # 1. 计算船到目标点的总距离
    dist_to_target = math.sqrt((target_x - current_x)**2 + (target_y - current_y)**2)
    
    # 2. 确定“虚拟目标点”（前视点）的位置
    # 如果离终点很近（小于前视距离），直接看终点；否则看前方10米处
    if dist_to_target <= lookahead_dist:
        look_x, look_y = target_x, target_y
    else:
        # 计算角度
        angle_to_target = math.atan2(target_y - current_y, target_x - current_x)
        # 沿着这个角度，向前截取前视距离，得到虚拟点坐标
        look_x = current_x + lookahead_dist * math.cos(angle_to_target)
        look_y = current_y + lookahead_dist * math.sin(angle_to_target)
    
    # 3. 计算期望航向角 (LOS Angle)
    # 这就是告诉舵机：“把船头转到这个角度！”
    los_angle = math.degrees(math.atan2(look_y - current_y, look_x - current_x))
    
    return los_angle, (look_x, look_y)

# --- 模拟运行过程 ---
print(f"{'步骤':<5} | {'当前位置 (x,y)':<15} | {'虚拟前视点':<15} | {'期望航向角':<10}")
print("-" * 60)

# 假设船被水流冲偏了一点，当前位置在 (0, -5)，而不是起点的 (0,0)
current_pos = (0, -5) 
target_pos = (100, 50)

for i in range(1, 4):
    # 调用LOS算法
    heading, virtual_point = calculate_los_heading(current_pos[0], current_pos[1], target_pos[0], target_pos[1], 10)
    
    print(f"{i:<5} | {str(current_pos):<15} | {str(virtual_point):<15} | {heading:.2f}°")
    
    # (模拟船向前开了一小步，这里简化处理，实际会结合动力学模型)
    # 假设船向虚拟点方向移动了5米
    import math
    move_angle = math.radians(heading)
    current_pos = (current_pos[0] + 5 * math.cos(move_angle), current_pos[1] + 5 * math.sin(move_angle))