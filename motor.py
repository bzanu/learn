import canopen
import time
import sys

# ================= 配置区域 =================
# 请将此处替换为你实际的 EDS 文件路径
EDS_FILE = 'kinco_servo.eds'  
NODE_ID = 1
CAN_CHANNEL = 'pcan0'  # Windows下通常用 '0', Linux下用 'can0' 或 'vcan0'
CAN_BITRATE = 500000
# =============================================

class ServoMotor:
    def __init__(self, node_id, eds_path):
        self.network = canopen.Network()
        # 加载节点，库会自动解析 EDS 文件
        self.node = self.network.add_node(node_id, eds_path)
        self.state = "INIT"

    def connect(self, channel, bitrate):
        self.network.connect(channel=channel, bustype='pcan', bitrate=bitrate)
        print(f"✅ 网络已连接: {channel}")

    def start_nmt(self):
        """发送 NMT 启动指令，让电机进入操作状态"""
        self.node.nmt.state = 'OPERATIONAL'
        print("🚀 发送 NMT 启动指令...")
        time.sleep(0.5)  # 等待驱动器响应

    def enable_servo(self):
        """
        标准的 CiA 402 状态机切换流程
        利用 EDS 解析出的对象字典名称来控制
        """
        print("⚡ 正在使能电机...")
        
        # 1. 切换到位置模式 (0x6060)
        # 注意：这里直接使用了 EDS 中定义的变量名 'Operation Mode'
        # 如果你的 EDS 里叫别的名字，请相应修改
        try:
            self.node.sdo['Operation Mode'].raw = 1  # 1 = 位置模式 (CSP/PP)
            print("   -> 已切换到位置模式")
        except KeyError:
            print("   ⚠️ 警告: EDS 中未找到 'Operation Mode'，尝试使用 0x6060")
            self.node.sdo[0x6060].raw = 1

        # 2. 状态机切换逻辑 (通过 0x6040 控制字)
        # 我们定义一个通用的使能序列
        control_sequence = [0x06, 0x07, 0x0F]
        
        for code in control_sequence:
            self.node.sdo['Controlword'].raw = code
            time.sleep(0.05) # 短暂延时等待驱动器处理
            
            # 检查状态字 (0x6041)
            status = self.node.sdo['Statusword'].raw
            # 简单的状态检查，0x237 代表 "Operation Enabled" (目标到达+使能)
            # 0x217 代表 "Switched On" (已上电)
            if not (status & 0x000F) == 0x07: 
                print(f"   ⚠️ 中间状态: 0x{status:X}")
        
        # 最后一次确认
        self.node.sdo['Controlword'].raw = 0x0F
        print("✅ 电机使能成功！")

    def move_to(self, position, wait=True):
        """
        移动到指定位置
        :param position: 目标位置 (脉冲数)
        :param wait: 是否等待到达后再返回
        """
        # 写入目标位置 (0x607A)
        self.node.sdo['Target Position'].raw = position
        print(f"🎯 目标位置设定为: {position}")

        if wait:
            # 简单的阻塞等待，直到状态字显示“目标到达”
            while True:
                status = self.node.sdo['Statusword'].raw
                # 检查位 10 (Target Reached)，即 0x0400
                if status & 0x0400:
                    print("   ✅ 到达目标")
                    break
                time.sleep(0.01)

    def disconnect(self):
        self.network.disconnect()

# ================= 主程序逻辑 =================

if __name__ == "__main__":
    # 1. 初始化电机对象
    motor = ServoMotor(NODE_ID, EDS_FILE)
    
    try:
        # 2. 连接 CAN 总线
        motor.connect(CAN_CHANNEL, CAN_BITRATE)
        
        # 3. 启动 NMT (这一步很关键，没有它无法通信)
        motor.start_nmt()
        
        # 4. 使能电机
        motor.enable_servo()
        
        # 5. 开始运动演示
        print("\n--- 开始运动演示 ---")
        
        # 运动 1: 走到 10000 的位置
        motor.move_to(10000)
        time.sleep(1)
        
        # 运动 2: 走到 -10000 的位置
        motor.move_to(-10000)
        time.sleep(1)
        
        # 运动 3: 回到原点
        motor.move_to(0)
        
        print("--- 演示结束 ---")

    except KeyboardInterrupt:
        print("\n🛑 用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
    finally:
        # 6. 断开连接
        motor.disconnect()
        print("🔌 连接已断开")