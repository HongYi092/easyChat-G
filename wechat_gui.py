import base64
import sys
import time
import keyboard
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QInputDialog, QDialog
from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPixmap
from ui_auto_wechat import WeChat
from module import ClockThread, MultiInputDialog, FileDialog, MyListWidget

# 将你的base64编码的图标字符串放在这里
icon_base64 = """
*****自己添加图标的地方******
"""

# 将base64编码的图标加载为QIcon
def load_icon():
    icon_data = QByteArray.fromBase64(icon_base64.encode("utf-8"))
    pixmap = QPixmap()
    pixmap.loadFromData(icon_data)
    return QIcon(pixmap)

class WechatGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.wechat = WeChat("C:\\Program Files\\Tencent\\WeChat\\WeChat.exe", locale="zh-CN")
        self.setWindowIcon(load_icon())
        self.clock = ClockThread()

        # 发消息的用户列表
        self.contacts = []

        # 初始化图形界面
        self.initUI()

        # 判断全局热键是否被按下
        self.hotkey_pressed = False
        keyboard.add_hotkey('ctrl+alt', self.hotkey_press)

    def initUI(self):
        # 垂直布局
        vbox = QVBoxLayout()
        # 显示微信exe路径
        self.path_label = QLabel("", self)
        self.path_label.setWordWrap(True)
        self.path_label.resize(self.width(), 100)

        # 选择微信exe路径的按钮
        self.path_btn = QPushButton("选择微信打开路径", self)
        self.path_btn.resize(self.path_btn.sizeHint())
        self.path_btn.clicked.connect(self.choose_path)

        self.open_wechat_btn = QPushButton("打开微信", self)
        self.open_wechat_btn.clicked.connect(self.open_wechat)

        # 添加聊天记录显示区域
        self.chat_history_view = QListWidget()
        self.chat_history_view.setFixedWidth(300)
        self.chat_history_view.itemDoubleClicked.connect(self.handle_item_double_click)

        # 添加输入框和按钮
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("输入用户名")
        self.message_input = QLineEdit(self)
        self.message_input.setPlaceholderText("输入消息内容")
        self.send_btn = QPushButton("发送消息并加载聊天记录", self)
        self.send_btn.clicked.connect(self.send_message_and_load_logs)

        contacts = self.init_choose_contacts()
        msg_widget = self.init_send_msg()
        clock = self.init_clock()

        hbox_main = QHBoxLayout()
        hbox_main.addWidget(self.chat_history_view)

        vbox_right = QVBoxLayout()
        vbox_right.addWidget(self.path_label)
        vbox_right.addWidget(self.path_btn)
        vbox_right.addWidget(self.open_wechat_btn)
        vbox_right.addWidget(self.name_input)
        vbox_right.addWidget(self.message_input)
        vbox_right.addWidget(self.send_btn)
        vbox_right.addLayout(contacts)
        vbox_right.addStretch(5)
        vbox_right.addLayout(msg_widget)
        vbox_right.addStretch(5)
        vbox_right.addLayout(clock)
        vbox_right.addStretch(1)

        hbox_main.addLayout(vbox_right)

        self.setLayout(hbox_main)
        self.setFixedSize(800, 700)  # 增加300像素宽度
        self.setWindowTitle('标题') # sorry 给姐姐代码里的标题的地方..
        self.setWindowIcon(load_icon())
        self.show()

    def hotkey_press(self):
        print("按下热键")   # 太多输出这个了..  我希望是按下热键后，窗口显示出来，并且自动聚焦到消息输入框
        self.show()
        self.activateWindow()
        self.raise_()  # 确保窗口在最前面
        self.message_input.setFocus()
        self.hotkey_pressed = True

    def init_choose_contacts(self):
        def save_contacts():
            path = QFileDialog.getSaveFileName(self, "保存联系人列表", "contacts.txt", "文本文件(*.txt)")[0]
            if not path == "":
                contacts = self.wechat.find_all_contacts()
                with open(path, 'w', encoding='utf-8') as f:    #可以改成a模式 追加但是不会创建新文件自己用的话就a模式挺好,个人感觉
                                                                #  大神略过就好
                    for contact in contacts:
                        f.write(contact + '\n')
                QMessageBox.information(self, "保存成功", "联系人列表保存成功！")

        def load_contacts():
            path = QFileDialog.getOpenFileName(self, "加载联系人列表", "", "文本文件(*.txt)")[0]
            if not path == "":
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f.readlines():
                        self.contacts_view.addItem(f"{self.contacts_view.count()+1}:{line.strip()}")
                QMessageBox.information(self, "加载成功", "联系人列表加载成功！")

        def add_contact():
            name_list, ok = QInputDialog.getText(self, '添加用户', '输入添加的用户名(可添加多个人名，用英文逗号,分隔):')
            if ok:
                if name_list != "":
                    names = name_list.split(',')
                    for name in names:
                        if self.contacts_view.count() < 1000:
                            id = f"{self.contacts_view.count() + 1}"
                            self.contacts_view.addItem(f"{id}:{str(name).strip()}")
                        else:
                            id = f"{self.contacts_view_2.count() + 1001}"
                            self.contacts_view_2.addItem(f"{id}:{str(name).strip()}")

        def del_contact():
            # 删除 contacts_view 中选中的项
            for i in range(self.contacts_view.count() - 1, -1, -1):
                if self.contacts_view.item(i).isSelected():
                    self.contacts_view.takeItem(i)

            # 为所有剩余的用户重新编号
            for i in range(self.contacts_view.count()):
                self.contacts_view.item(i).setText(f"{i+1}:{self.contacts_view.item(i).text().split(':')[1]}")

            # 删除 contacts_view_2 中选中的项
            for i in range(self.contacts_view_2.count() - 1, -1, -1):
                if self.contacts_view_2.item(i).isSelected():
                    self.contacts_view_2.takeItem(i)

            # 重新编号 contacts_view_2 中的项，从 1001 开始 因为一下出所有的选择起来有点麻烦,
            # 所以就搞了2列, 并且 可以双击就可以发送
            for i in range(self.contacts_view_2.count()):
                self.contacts_view_2.item(i).setText(f"{i + 1001}:{self.contacts_view_2.item(i).text().split(':')[1]}")

        hbox = QHBoxLayout()

        # 左边的用户列表
        self.contacts_view = MyListWidget()
        self.contacts_view_2 = MyListWidget()
        self.clock.contacts = self.contacts_view
        self.clock.contacts = self.contacts_view_2
        for name in self.contacts:
            self.contacts_view.addItem(name)
            self.contacts_view_2.addItem(name)
        self.contacts_view.itemDoubleClicked.connect(self.add_to_special_contacts)

        hbox.addWidget(self.contacts_view)
        hbox.addWidget(self.contacts_view_2)

        vbox = QVBoxLayout()
        vbox.stretch(1)

        info = QLabel("待发送用户列表")
        save_btn = QPushButton("保存微信好友列表")
        save_btn.clicked.connect(save_contacts)
        load_btn = QPushButton("加载用户txt文件")
        load_btn.clicked.connect(load_contacts)
        add_btn = QPushButton("添加用户")
        add_btn.clicked.connect(add_contact)
        del_btn = QPushButton("删除用户")
        del_btn.clicked.connect(del_contact)

        # 设置按钮的最大宽度和高度
        max_width = 200
        max_height = 50
        for btn in [save_btn, load_btn, add_btn, del_btn]:
            btn.setMaximumWidth(max_width)
            btn.setMaximumHeight(max_height)

        vbox.addWidget(info)
        vbox.addWidget(save_btn)
        vbox.addWidget(load_btn)
        vbox.addWidget(add_btn)
        vbox.addWidget(del_btn)
        hbox.addLayout(vbox)

        return hbox

    def add_to_special_contacts(self, item):
        # 获取双击的联系人信息
        contact_info = item.text()

        # 从 contacts_view 中删除该联系人
        self.contacts_view.takeItem(self.contacts_view.row(item))

        # 添加到 contacts_view_2 中
        self.contacts_view_2.addItem(contact_info)

        # 重新编号 contacts_view 中的联系人
        for i in range(self.contacts_view.count()):
            self.contacts_view.item(i).setText(f"{i + 1}:{self.contacts_view.item(i).text().split(':')[1]}")

        # 重新编号 contacts_view_2 中的联系人
        for i in range(self.contacts_view_2.count()):
            self.contacts_view_2.item(i).setText(f"{i + 1}:{self.contacts_view_2.item(i).text().split(':')[1]}")

    def init_clock(self):
        def add_contact():
            inputs = [
                "年 (例：2024)",
                "月 (1~12)",
                "日 (1~31)",
                "小时（0~23）",
                "分钟 (0~59)",
                "发送信息的起点（从哪一条开始发）",
                "发送信息的终点（到哪一条结束，包括该条）",
            ]

            local_time = time.localtime(time.time())
            default_values = [
                str(local_time.tm_year),
                str(local_time.tm_mon),
                str(local_time.tm_mday),
                str(local_time.tm_hour),
                str(local_time.tm_min),
                "",
                "",
            ]

            dialog = MultiInputDialog(inputs, default_values)
            if dialog.exec() == QDialog.Accepted:
                year, month, day, hour, min, st, ed = dialog.get_input()
                if year == "" or month == "" or day == "" or hour == "" or min == "" or st == "" or ed == "":
                    QMessageBox.warning(self, "输入错误", "输入不能为空！")
                    return
                else:
                    input = f"{year} {month} {day} {hour} {min} {st}-{ed}"
                    self.time_view.addItem(input)

        def del_contact():
            for i in range(self.time_view.count() - 1, -1, -1):
                if self.time_view.item(i).isSelected():
                    self.time_view.takeItem(i)

        def start_counting():
            if self.clock.time_counting is True:
                return
            else:
                self.clock.time_counting = True
            info.setStyleSheet("color:red")
            info.setText("定时发送（目前已开始）")
            self.clock.start()

        def end_counting():
            self.clock.time_counting = False
            info.setStyleSheet("color:black")
            info.setText("定时发送（目前未开始）")

        def prevent_offline():
            if self.clock.prevent_offline is True:
                self.clock.prevent_offline = False
                prevent_btn.setStyleSheet("color:black")
                prevent_btn.setText("防止自动下线：（目前关闭）")
            else:
                # 弹出提示框
                QMessageBox.information(self, "防止自动下线", "防止自动下线已开启！每隔一小时自动点击微信窗口，防"
                                                              "止自动下线。请不要在正常使用电脑时使用该策略。")

                self.clock.prevent_offline = True
                prevent_btn.setStyleSheet("color:red")
                prevent_btn.setText("防止自动下线：（目前开启）")

        hbox = QHBoxLayout()

        # 左边的用户列表
        self.time_view = MyListWidget()
        self.clock.clocks = self.time_view
        hbox.addWidget(self.time_view)

        # 右边的按钮界面,保持没有动原作者的布局
        vbox = QVBoxLayout()
        vbox.stretch(1)

        info = QLabel("定时发送（目前未开始）")
        add_btn = QPushButton("添加时间")
        add_btn.clicked.connect(add_contact)
        del_btn = QPushButton("删除时间")
        del_btn.clicked.connect(del_contact)
        start_btn = QPushButton("开始定时")
        start_btn.clicked.connect(start_counting)
        end_btn = QPushButton("结束定时")
        end_btn.clicked.connect(end_counting)
        prevent_btn = QPushButton("防止自动下线：（目前关闭）")
        prevent_btn.clicked.connect(prevent_offline)

        vbox.addWidget(info)
        vbox.addWidget(add_btn)
        vbox.addWidget(del_btn)
        vbox.addWidget(start_btn)
        vbox.addWidget(end_btn)
        vbox.addWidget(prevent_btn)
        hbox.addLayout(vbox)

        return hbox

    # 发送消息内容界面的初始化
    def init_send_msg(self):
        # 从txt中加载消息内容
        def load_text():
            path = QFileDialog.getOpenFileName(self, "加载内容文本", "", "文本文件(*.txt)")[0]
            if not path == "":
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f.readlines():
                        self.msg.addItem(f"{self.msg.count()+1}:text:{line.strip()}")
                QMessageBox.information(self, "加载成功", "内容文本加载成功！")

        def add_text():
            inputs = ["请指定发送给哪些用户(1,2,3代表发送给前三位用户)，如需全部发送请忽略此项",
                      "请输入发送的内容"]
            dialog = MultiInputDialog(inputs)
            if dialog.exec() == QDialog.Accepted:
                to, text = dialog.get_input()
                to = "all" if to == "" else to
                if text != "":
                    rank = self.msg.count() + 1
                    if text[:3] == "at:":
                        self.msg.addItem(f"{rank}:at:{to}:{str(text[3:])}")
                    else:
                        self.msg.addItem(f"{rank}:text:{to}:{str(text)}")

        def add_file():
            dialog = FileDialog()
            if dialog.exec() == QDialog.Accepted:
                to, path = dialog.get_input()
                to = "all" if to == "" else to
                if path != "":
                    self.msg.addItem(f"{self.msg.count()+1}:file:{to}:{str(path)}")

        def del_content():
            for i in range(self.msg.count() - 1, -1, -1):
                if self.msg.item(i).isSelected():
                    self.msg.takeItem(i)
            for i in range(self.msg.count()):
                self.msg.item(i).setText(f"{i+1}:"+self.msg.item(i).text().split(':', 1)[1])

        def send_msg(gap=None, st=None, ed=None):
            self.hotkey_pressed = False
            try:
                if st is None:
                    st = 1
                    ed = self.msg.count()
                for user_i in range(self.contacts_view.count()):
                    rank, name = self.contacts_view.item(user_i).text().split(':', 1)
                for user_i in range(self.contacts_view_2.count()):
                    rank, name = self.contacts_view_2.item(user_i).text().split(':', 1)
                    for msg_i in range(st-1, ed):
                        if self.hotkey_pressed is True:
                            QMessageBox.warning(self, "发送失败", f"热键已按下，已停止发送！")
                            return
                        msg = self.msg.item(msg_i).text()
                        _, type, to, content = msg.split(':', 3)
                        if to == "all" or str(rank) in to.split(','):
                            if type == "text":
                                self.wechat.send_msg(name, content)
                            elif type == "file":
                                self.wechat.send_file(name, content)
                            elif type == "at":
                                self.wechat.at(name, content)
            except Exception:
                QMessageBox.warning(self, "发送失败", f"发送失败！请检查内容格式或是否有遗漏步骤！")
                return

        vbox_left = QVBoxLayout()
        info = QLabel("添加要发送的内容（程序将按顺序发送）")
        self.msg = MyListWidget()
        self.clock.send_func = send_msg
        self.clock.prevent_func = self.wechat.prevent_offline
        send_btn = QPushButton("发送")
        send_btn.clicked.connect(send_msg)

        vbox_left.addWidget(info)
        vbox_left.addWidget(self.msg)
        vbox_left.addWidget(send_btn)

        vbox_right = QVBoxLayout()
        vbox_right.stretch(1)

        load_btn = QPushButton("加载内容txt文件")
        load_btn.clicked.connect(load_text)
        text_btn = QPushButton("添加文本内容")
        text_btn.clicked.connect(add_text)
        file_btn = QPushButton("添加文件")
        file_btn.clicked.connect(add_file)
        del_btn = QPushButton("删除内容")
        del_btn.clicked.connect(del_content)

        vbox_right.addWidget(load_btn)
        vbox_right.addWidget(text_btn)
        vbox_right.addWidget(file_btn)
        vbox_right.addWidget(del_btn)

        # 整体布局
        hbox = QHBoxLayout()
        hbox.addLayout(vbox_left)
        hbox.addLayout(vbox_right)

        return hbox

    def load_chat_history(self, name):
        self.chat_history_view.clear()
        logs = self.wechat.get_dialogs(name, 50)
        for log in logs:
            log_type, user, content = log    # 这里的log是一个元组
            if log_type == '时间信息':
                log_text = f"时间信息: {content}"
            elif log_type == '用户发送':
                log_text = f"{user} 发送: {content}"
            else:
                log_text = f"{log_type}: {content}"

            item = QListWidgetItem(log_text)
            if content.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):  # 如果是图片/动图之类的
                item.setData(Qt.UserRole, content)
            self.chat_history_view.addItem(item)

    def send_message_and_load_logs(self):
        name = self.name_input.text().strip()
        msg = self.message_input.text().strip()
        if name and msg:
            self.wechat.send_msg(name, msg)
            self.load_chat_history(name)
        else:
            QMessageBox.warning(self, "输入错误", "请输入有效的用户名和消息内容。")

    def handle_item_double_click(self, item):
        content = item.data(Qt.UserRole)
        if content and content.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')): # 如果是图片/动图之类的
            self.show_image(content)
        else:
            new_content, ok = QInputDialog.getText(self, "编辑内容", "修改消息内容:", QLineEdit.Normal, item.text())
            if ok and new_content:
                item.setText(new_content)

    def show_image(self, image_path):
        dlg = QDialog(self)
        dlg.setWindowTitle("图片查看")  # 这里的标题也是我自己加的 但是在界面上还没有显示出来 担心会有人反感 如果想要的话 可以在下面直接补充就可以显示
        vbox = QVBoxLayout()
        lbl = QLabel()
        pixmap = QPixmap(image_path)
        lbl.setPixmap(pixmap)
        vbox.addWidget(lbl)
        dlg.setLayout(vbox)
        dlg.exec()

    def choose_path(self):
        path = QFileDialog.getOpenFileName(self, '打开文件', '/home')[0]
        if path != "":
            self.path_label.setText(path)
            self.wechat.path = path
            print("选定的路径:", path)
        else:
            QMessageBox.warning(self, "错误", "未选择有效的文件路径。")

    def open_wechat(self):
        self.wechat.open_wechat()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WechatGUI()
    sys.exit(app.exec())
