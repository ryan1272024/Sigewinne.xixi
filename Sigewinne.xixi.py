import sys
import os
import math
from PyQt5 import QtWidgets, QtGui, QtCore

class Pet(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(QtWidgets.QApplication.desktop().screenGeometry())

        self.pet_x = 300
        self.pet_y = 300
        self.speed = 5
        self.min_distance = 50

        self.state = 'idle'
        self.frames = []
        self.frame_index = 0
        self.flip = False

        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(self.pet_x, self.pet_y, 200, 200)
        self.label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
        self.label.mousePressEvent = self.on_click

        self.load_frames("idle", 1)

        self.anim_timer = QtCore.QTimer()
        self.anim_timer.timeout.connect(self.update_frame)
        self.anim_timer.start(50)

        self.move_timer = QtCore.QTimer()
        self.move_timer.timeout.connect(self.move_towards_mouse)
        self.move_timer.start(50)

        self.create_tray_icon()

    def load_frames(self, prefix, count, flip=False):
        self.frames = []
        self.frame_index = 0
        self.flip = flip
        for i in range(1, count + 1):
            path = os.path.join("static_gifs", f"{prefix}_{i}.gif")
            if os.path.exists(path):
                img = QtGui.QImage(path)
                if flip:
                    img = img.mirrored(True, False)
                img = img.scaled(200, 200, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.frames.append(QtGui.QPixmap.fromImage(img))
        if not self.frames:
            print(f"未找到 {prefix} 的帧图像！")

    def update_frame(self):
        if self.frames:
            self.label.setPixmap(self.frames[self.frame_index])
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def on_click(self, event):
        if self.state != "raise":
            self.load_frames("raise", 50, flip=self.flip)
            self.state = "raise"
            QtCore.QTimer.singleShot(2500, self.reset_after_raise)

    def reset_after_raise(self):
        self.state = "idle"
        self.load_frames("idle", 1, flip=self.flip)

    def move_towards_mouse(self):
        if self.state == "raise":
            return  # 不移动，只播放raise动画

        cursor_pos = QtGui.QCursor.pos()
        mouse_x, mouse_y = cursor_pos.x(), cursor_pos.y()

        dx = mouse_x - self.pet_x
        dy = mouse_y - self.pet_y
        distance = math.hypot(dx, dy)

        if distance < self.min_distance:
            if self.state != "idle":
                self.load_frames("idle", 1, flip=self.flip)
                self.state = "idle"
            return
        else:
            if dx < 0 and not self.flip:
                self.load_frames("walk", 38, flip=True)
                self.flip = True
                self.state = "walk"
            elif dx > 0 and self.flip:
                self.load_frames("walk", 38, flip=False)
                self.flip = False
                self.state = "walk"
            elif self.state != "walk":
                self.load_frames("walk", 38, flip=self.flip)
                self.state = "walk"

            move_x = dx / distance * self.speed
            move_y = dy / distance * self.speed

            self.pet_x += move_x
            self.pet_y += move_y

            screen_rect = self.screen().availableGeometry()
            self.pet_x = max(0, min(self.pet_x, screen_rect.width() - 200))
            self.pet_y = max(0, min(self.pet_y, screen_rect.height() - 200))

            self.label.move(int(self.pet_x), int(self.pet_y))

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-repeat: no-repeat;
                background-position: center;
                border: none;  /* 去除边框 */
                padding: 0px;
                border-radius: 12px;
                color: pink;
                font-size: 14px;
            }

            QMenu::item {
                background-color: white;
                padding: 8px 20px;
            }

            QMenu::item:selected {
                background-color: white;
                color: #FFB6C1;
                border-radius: 0px;
            }
        """)

        hide_action = menu.addAction("隐藏桌宠")
        exit_action = menu.addAction("退出桌宠")

        # 获取桌宠当前的左上角位置
        pet_position = self.label.pos()

        # 计算菜单位置，桌宠的左上方
        menu_position = QtCore.QPoint(pet_position.x(), pet_position.y() - menu.height())

        # 显示菜单并获取点击的操作
        action = menu.exec_(menu_position)

        if action == hide_action:
            self.hide()
        elif action == exit_action:
            QtWidgets.qApp.quit()

    def create_tray_icon(self):
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        icon = QtGui.QIcon(os.path.join("static_gifs", "idle_1.gif"))
        self.tray_icon.setIcon(icon)

        tray_menu = QtWidgets.QMenu()
        show_action = tray_menu.addAction("显示桌宠")
        exit_action = tray_menu.addAction("退出")

        show_action.triggered.connect(self.show)
        exit_action.triggered.connect(QtWidgets.qApp.quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    pet = Pet()
    pet.show()
    sys.exit(app.exec_())
