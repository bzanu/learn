import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout,QLabel,QLineEdit,QDesktopWidget,QGroupBox,QRadioButton
class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.center()

        # layout = QVBoxLayout()
        # layout.addStretch(10)  # 添加弹性空间
        # btn1 = QPushButton('Button 1', self)
        # btn2 = QPushButton('Button 2', self)
        # layout.addWidget(btn1)
        # layout.addWidget(btn2)
        
        # self.setLayout(layout)

    def initUI(self):
        self.setWindowTitle('PyQt Example')#设置标题
        self.resize(600, 300)

        btn = QPushButton('Click Me', self)
        btn.setGeometry(0, 40, 100, 20) #x, y, width, height

        label = QLabel('Hello PyQt!', self)
        label.setGeometry(0, 0, 80, 20)#x, y, width, height

        edit = QLineEdit(self)
        edit.setPlaceholderText('Enter text here')
        edit.setGeometry(0, 20, 200, 20)
        
        container = QVBoxLayout()
        container.addStretch()  # 添加弹性空间
        #创建第一个组，添加多个组件
        hobby_box = QGroupBox('Hobbies')
        hobby_layout = QVBoxLayout()
        btn1 = QRadioButton('Reading')
        btn2 = QRadioButton('Traveling')
        btn3 = QRadioButton('Cooking')
        hobby_layout.addWidget(btn1)
        hobby_layout.addWidget(btn2)
        hobby_layout.addWidget(btn3)
        hobby_box.setLayout(hobby_layout)

        #创建第二个组，添加多个组件
        gender_box = QGroupBox("Gender")
        gender_layout = QVBoxLayout()
        male_btn = QRadioButton("Male")
        female_btn = QRadioButton("Female")
        gender_layout.addWidget(male_btn)
        gender_layout.addWidget(female_btn)
        gender_box.setLayout(gender_layout)

        container.addWidget(hobby_box)
        container.addWidget(gender_box)
        self.setLayout(container)

    def center(self):
            #调整窗口在屏幕中央显示
        center_pointer = QDesktopWidget().availableGeometry().center()
        x =center_pointer.x()
        y =center_pointer.y()
        old_x,old_y,width,height = self.frameGeometry().getRect()
        self.move(x - width // 2, y - height // 2)

def main():
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    app.exec_()

if __name__ == '__main__':
    main()