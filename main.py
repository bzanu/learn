import time
from serial_syf import Serial as ser
from thread_syf import task   
datasend = bytes([0x41,0x42,0x43,0x44,0x45,0x0A])#换行是0x0A,回车是0x0D
startcmd = bytes([0x32, 0x01, 0x08, 0x70, 0x00, 0x00, 0x00, 0x55, 0xF0])#启动命令
stopcmd = bytes([0x32, 0x01, 0x09, 0x00, 0x00, 0x00, 0x00, 0xC4, 0xF0])#停止命令
             
def main():
    try:
        com = ser('COM26', 115200)
        task_receive = task(com.receive_data)#创建线程对象，传入接收数据的函数
        task_receive.start()#启动接收线程
        com.send_data(startcmd)#发送启动命令
        while True:
            time.sleep(1)         
    except KeyboardInterrupt:
        com.send_data(stopcmd)#发送停止命令
        task_receive.stop() #一定要先关线程，再退出程序，否则会出现多线程竞争资源问题
        com.close_serial()
        print("用户终止")
    finally:
        print("程序已退出")
        

if __name__ == "__main__":
    main()