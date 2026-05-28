"""
使用 python-can 库进行 PCAN 通讯
兼容 Windows/Linux，API 统一
"""

import can
import time
import threading


class PythonCANDevice:
    """基于 python-can 的 PCAN 封装"""
    
    def __init__(self, channel='PCAN_USBBUS1', bitrate=500000):
        self.channel = channel
        self.bitrate = bitrate
        self.bus = None
        self.running = False
        self.receive_thread = None
        self.callback = None
    
    def connect(self):
        """连接 PCAN"""
        try:
            self.bus = can.interface.Bus(
                channel=self.channel,
                bustype='pcan',
                bitrate=self.bitrate
            )
            print(f"[OK] 已连接 {self.channel} @ {self.bitrate/1000:.0f}Kbps")
            return True
        except Exception as e:
            print(f"[ERROR] 连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        self.running = False
        if self.receive_thread:
            self.receive_thread.join(timeout=1.0)
        if self.bus:
            self.bus.shutdown()
            print("[OK] 已断开")
    
    def send(self, can_id, data, is_extended=False):
        """发送 CAN 报文"""
        if not self.bus:
            print("[ERROR] 未连接")
            return False
        
        msg = can.Message(
            arbitration_id=can_id,
            data=data,
            is_extended_id=is_extended
        )
        
        try:
            self.bus.send(msg)
            hex_data = ' '.join(f'{b:02X}' for b in data)
            id_str = f"{can_id:08X}" if is_extended else f"{can_id:03X}"
            print(f"[TX] ID=0x{id_str}  Data=[{hex_data}]")
            return True
        except can.CanError as e:
            print(f"[ERROR] 发送失败: {e}")
            return False
    
    def receive(self, timeout=0.1):
        """接收单条报文"""
        if not self.bus:
            return None
        
        msg = self.bus.recv(timeout=timeout)
        if msg is None:
            return None
        
        hex_data = ' '.join(f'{b:02X}' for b in msg.data)
        id_str = f"{msg.arbitration_id:08X}" if msg.is_extended_id else f"{msg.arbitration_id:03X}"
        print(f"[RX] ID=0x{id_str}  Data=[{hex_data}]  DLC={msg.dlc}")
        
        return msg
    
    def start_receive_thread(self, callback=None):
        """启动后台接收"""
        self.running = True
        self.callback = callback
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
        print("[OK] 接收线程已启动")
    
    def _receive_loop(self):
        """接收循环"""
        while self.running:
            msg = self.receive(timeout=0.1)
            if msg and self.callback:
                self.callback(msg)
    
    def send_periodic(self, can_id, data, period_sec, is_extended=False):
        """发送周期性报文 (由 python-can 内部调度)"""
        msg = can.Message(
            arbitration_id=can_id,
            data=data,
            is_extended_id=is_extended
        )
        task = self.bus.send_periodic(msg, period_sec)
        print(f"[OK] 已启动周期性发送 ID=0x{can_id:03X} 周期={period_sec}s")
        return task  # 保持 task 引用，停止时调用 task.stop()


# ==================== 使用示例 ====================

def on_message(msg):
    """接收回调"""
    hex_data = ' '.join(f'{b:02X}' for b in msg.data)
    print(f"  [回调] ID=0x{msg.arbitration_id:03X} Data=[{hex_data}]")


if __name__ == "__main__":
    # 使用 python-can
    dev = PythonCANDevice(channel='PCAN_USBBUS1', bitrate=500000)
    
    if not dev.connect():
        exit(1)
    
    try:
        dev.start_receive_thread(callback=on_message)
        
        # 周期性发送 (10Hz)
        task = dev.send_periodic(0x100, [0x01, 0x02, 0x03, 0x04], 0.1)
        
        # 同时手动发送
        counter = 0
        while True:
            dev.send(0x200, [counter & 0xFF, 0xAA, 0xBB])
            counter += 1
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print("\n--- 停止 ---")
        task.stop()
    finally:
        dev.disconnect()