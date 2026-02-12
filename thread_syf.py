import threading
"""
此为线程库，提供一个task类用于创建和管理线程，目前仅包含启动和停止线程的方法，后续可以根据需要添加更多功能，如线程状态检查、异常处理等。
由syf编写，日期2026-02-12
使用时只需要将task函数传入即可
使用示例：
创建线程对象：TASK = task(function)  其中function是你想在线程中执行的函数，可以是串口接收数据的函数，也可以是其他需要在后台运行的任务。
启动线程：TASK.start()
停止线程：TASK.stop()
"""

class task:
    def __init__(self,target_task):
        self.target_task = target_task

    def start(self):
        self.thread = threading.Thread(target=self.target_task)
        self.thread.daemon = True
        self.thread.start()
        print("线程已启动")
    def stop(self):
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
            print("线程已停止")
