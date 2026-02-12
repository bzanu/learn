import serial
import time
import struct
"""
该串口库为syf编写,日期2026-02-12
功能1.打开串口并设置参数
功能2.发送数据
功能3.接收数据并解析
功能4.关闭串口
用于接收固定长度串口数据包，目前接收数据包长度为73字节，数据帧头为0x01 0x32 0x08，数据帧尾为0xF0
可以更改以下内容：
self.datahead = bytes([0x01,0x32,0x08])#数据帧头
self.datatail = 0xF0  #数据帧尾
self.datasize = 73   #数据帧长度73字节
"""

class Serial:
    def __init__(self, port, baud):#串口需要有端口，波特率，数据位大小，校验位，停止位
        self.port = port
        self.baud = baud
        self.datasize = serial.EIGHTBITS  #8代表8位数据位
        self.parity = serial.PARITY_NONE  #'N'代表无校验
        self.stopbits = serial.STOPBITS_ONE  #1代表1位停止位
        self.timeout = 0.1
        self.serial_object = serial.Serial(port=self.port,
                                           baudrate=self.baud,bytesize=self.datasize,
                                           parity=self.parity,stopbits=self.stopbits,timeout=self.timeout)
        self.receive_thread_flag = False #接收线程标志位,暂时没用上
        self.datahead = bytes([0x01,0x32,0x08])#数据帧头
        self.datatail = 0xF0  #数据帧尾
        self.data_size = 73   #数据帧长度73字节
        print(f"串口{self.port}已打开,波特率为{self.baud}")
    def send_data(self,data_bytes):
        self.serial_object.write(data_bytes)
        print(f"发送数据: {' '.join(f'{b:02X}' for b in data_bytes)},数据长度为{len(data_bytes)}字节")
    def close_serial(self):
        if self.serial_object.is_open:
            self.serial_object.close()
            print(f"串口{self.port}已关闭")
    def find_data(self,data_buf):
        '''
若header_pos返回 -1:表示当前缓冲区未找到帧头（函数会保留末尾最多两个字节以便下次继续匹配）。
若header_pos返回 >=0:表示帧头从该索引开始，接着代码会检查从该位置到 header_pos + datasize 是否有完整帧；若完整且尾字节为 datatail 则提取为一帧并返回。
        '''
        header_pos = data_buf.find(self.datahead)#在缓冲区中查找帧头位置
        if header_pos == -1:          #如果返回值为-1，表示在data_buf中未找到帧头
            if len(data_buf) > 2:    
                return False, None, data_buf[-2:]
            return False, None, data_buf
        if len(data_buf) < header_pos + self.data_size: #如果缓冲区长度不足以包含完整帧，也是没找到完整数据帧
            return False, None, data_buf
        frame_data = data_buf[header_pos:header_pos + self.data_size]#当data_buf中存在数据帧头，并且缓冲区长度足够时，提取完整数据帧
        #然后将数据帧存放在frame_data中
        if frame_data[-1] == self.datatail:   #检验数据帧尾是否正确
            remaining = data_buf[header_pos + self.data_size:]#如果数据帧尾正确，那就把切除完整数据帧以外剩余的数据存放在remaining中，用于下一轮解析
            return True, frame_data, remaining
        else:
            return False, None, data_buf[header_pos + 1:]#如果数据帧尾不正确，则继续在剩余数据中查找下一帧

    def process_data(self,frame_data):
        #在这里处理接收到的数据帧
        if len(frame_data) != 73:
            print(f"错误: 数据帧长度应为73字节，实际为{len(frame_data)}字节")
            return None
        try:
            #使用小端顺序解析数据帧
            timestamp = struct.unpack('<I', frame_data[3:7])[0] #时间戳，4字节无符号整数,从73字节数据帧第3字节开始到第6字节
            acc_x = struct.unpack('<i', frame_data[19:23])[0]   #加速度X轴，4字节有符号整数
            acc_y = struct.unpack('<i', frame_data[23:27])[0]    #加速度Y轴，4字节有符号整数
            acc_z = struct.unpack('<i', frame_data[27:31])[0]    #加速度Z轴，4字节有符号整数
            gyro_x = struct.unpack('<i', frame_data[31:35])[0]   #陀螺仪X轴，4字节有符号整数
            gyro_y = struct.unpack('<i', frame_data[35:39])[0]    #陀螺仪Y轴，4字节有符号整数
            gyro_z = struct.unpack('<i', frame_data[39:43])[0]    #陀螺仪Z轴，4字节有符号整数
            pitch = struct.unpack('<f', frame_data[55:59])[0]     #姿态角Pitch，4字节有符号整数
            roll = struct.unpack('<f', frame_data[59:63])[0]      #姿态角Roll，4字节有符号整数
            gravity_inclination = struct.unpack('<f', frame_data[63:67])[0]   #重力倾角，4字节有符号整数

            pitch = round(pitch, 2)  #分别保留两位小数
            roll = round(roll, 2)
            gravity_inclination = round(gravity_inclination, 2)

            elapsed_time_us = struct.unpack('<I', frame_data[67:71])[0]  #算法执行时间，4字节无符号整数
            print(f"\n时间戳：{timestamp} ms,加速度xyz:{acc_x},{acc_y},{acc_z} mg,陀螺仪xyz:{gyro_x},{gyro_y},{gyro_z} mdps,角度pitch:{pitch} deg,roll:{roll} deg,重力倾角:{gravity_inclination} deg,算法执行时间:{elapsed_time_us} us\n")
        except struct.error as e:
            print(f"数据解析错误: {e}")
            return None
    def receive_data(self):
        buffer = b''
        while True:
            
            if self.serial_object and self.serial_object.in_waiting > 0:
                datareceive = self.serial_object.read(self.serial_object.in_waiting)
                buffer += datareceive
                while True:
                    found, frame, buffer = self.find_data(buffer)
                    if found:
                        print(f"接收数据: {' '.join(f'{b:02X}' for b in frame)},数据长度为{len(frame)}字节")
                        self.process_data(frame)
                    else:
                        break
            if len(buffer) > 1024: #防止缓冲区无限增大,每次只保留最后256字节
                buffer = buffer[-256:]
            time.sleep(0.01)