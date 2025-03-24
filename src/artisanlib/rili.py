from PyQt6.QtWidgets import (QWidget, QLabel, QComboBox, QPushButton,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QDialog)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QPixmap, QPainter
from datetime import datetime
import calendar
import os

global_calendar = None  # 全局变量

class Calendar(QDialog):
    def __init__(self, parent=None, on_date_selected=None, special_dates=None):
        super().__init__(parent)
        self.on_date_selected = on_date_selected
        self.special_dates = special_dates or []

        self.script_path = os.path.abspath(__file__)
        self.script_dir = os.path.dirname(self.script_path)
        self.parent_dir = os.path.dirname(self.script_dir)
        self.normalized_path = self.parent_dir.replace('\\', '/')

        # 设置窗口属性
        self.setFixedSize(300, 320)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
        )

        # 设置背景透明
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 设置背景图片
        self.bg_image = QPixmap(self.normalized_path + '/includes/Icons/general/lsbj.png')

        # 初始化日期
        self.current_date = QDate.currentDate()
        self.year = self.current_date.year()
        self.month = self.current_date.month()

        # 创建布局
        self.create_calendar()

        # 设置点击外部关闭
        #self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.bg_image)

    def focusOutEvent(self, event):
        # 当窗口失去焦点时关闭
        self.close()
        super().focusOutEvent(event)

    def create_calendar(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(0)  # 减少垂直间距

        # 年月选择部分
        date_frame = QWidget()
        date_frame.setFixedHeight(35)  # 固定高度
        date_layout = QHBoxLayout(date_frame)
        date_layout.setContentsMargins(0, 0, 0, 0)
        xialaIMG = f"{self.normalized_path}/includes/Icons/general/xiala2.png"
        # 定义统一的样式
        combo_style = f"""
                     QComboBox {{
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    background: white;
                    color: black;
                    text-align: center;
                    text-align-last: center;
                    text-align-vertical: center;
                }}
                QComboBox:editable {{
                    background: white;
                }}
                QComboBox:focus {{
                    outline: none;
                    border: 1px solid #CCCCCC; /* 保持边框样式 */
                }}
                QComboBox QLineEdit {{
                    border: none;  /* 移除 QLineEdit 的边框 */
                    background: transparent; /* 让背景透明 */
                }}
                QComboBox QLineEdit:focus {{
                    border: none;
                    outline: none;
                }}
                QComboBox QAbstractItemView::item:focus {{
                    border: none;
                    outline: none;
                    background: white;
                }}
                QComboBox::drop-down {{
                    border-left: 1px solid #CCCCCC;
                    border-top-right-radius: 5px;
                    border-bottom-right-radius: 5px;
                    background: white;
                    width: 20px;
                    color: black;
                }}
                QComboBox::down-arrow {{
                    width: 5;
                    height: 5;
                    background-Image: url(".venv/xiala.png");    
                }}
                QComboBox QAbstractItemView {{
                    outline: none;
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    background: #808080;
                    selection-background-color: #D3D3D3;
                    border: 1px solid #FFFFFF;
                    color: black;
                }}
                QComboBox QAbstractItemView::item {{
                    height: 25px;
                    padding-left: 5px;
                    background-color: #FFFFFF;
                    color: black;
                    min-width: 150px;
                }}
                QComboBox QAbstractItemView::item:hover {{
                    background-color: #CCCCCC;
                    color: #808080;
                }}
                QComboBox QAbstractItemView::item:selected {{
                    border: none;
                }}

                """

        # 年份选择
        self.year_combo = QComboBox()
        self.year_combo.addItems([str(year) for year in range(self.year - 10, self.year + 11)])
        self.year_combo.setCurrentText(str(self.year))
        self.year_combo.setEditable(True)  # 设置为可编辑
        self.year_combo.lineEdit().setReadOnly(True)  # 设置为只读
        self.year_combo.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置文本居中
        self.year_combo.currentTextChanged.connect(self.on_year_changed)
        self.year_combo.setFixedWidth(80)
        self.year_combo.setStyleSheet(combo_style)
        # 月份选择
        self.month_combo = QComboBox()
        self.month_combo.addItems([str(month) for month in range(1, 13)])
        self.month_combo.setCurrentText(str(self.month))
        self.month_combo.setEditable(True)
        self.month_combo.lineEdit().setReadOnly(True)
        self.month_combo.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.month_combo.currentTextChanged.connect(self.on_month_changed)
        self.month_combo.setFixedWidth(55)
        self.month_combo.setStyleSheet(combo_style)

        year_label = QLabel("年")
        # year_label.setStyleSheet("padding: 0px 5px;")  # 设置左右边距
        month_label = QLabel("月")
        # month_label.setStyleSheet("padding: 0px 5px;")  # 设置左右边距
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(5)
        date_layout.addWidget(self.year_combo)
        date_layout.addWidget(year_label)
        date_layout.addWidget(self.month_combo)
        date_layout.addWidget(month_label)
        # date_layout.addStretch()

        # 前后月份按钮，设置透明背景
        prev_btn = QPushButton("<")
        next_btn = QPushButton(">")
        prev_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
        """)
        next_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
        """)
        prev_btn.clicked.connect(self.prev_month)
        next_btn.clicked.connect(self.next_month)

        date_layout.addWidget(prev_btn)
        date_layout.addSpacing(10)
        date_layout.addWidget(next_btn)

        main_layout.addWidget(date_frame)

        # 星期标题部分
        days_frame = QWidget()
        days_frame.setFixedHeight(35)  # 固定高度
        days_layout = QHBoxLayout(days_frame)
        days_layout.setContentsMargins(0, 0, 0, 0)
        days_layout.setSpacing(0)

        # 星期标题
        days = ['日', '一', '二', '三', '四', '五', '六']
        for day in days:
            label = QLabel(day)
            label.setFixedSize(35, 35)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    color: black;
                    background: transparent;
                }
            """)
            days_layout.addWidget(label)

        main_layout.addWidget(days_frame)

        # 日期部分
        calendar_frame = QWidget()
        calendar_layout = QGridLayout(calendar_frame)
        calendar_layout.setContentsMargins(0, 0, 0, 0)
        calendar_layout.setHorizontalSpacing(0)  # 设置水平间距
        calendar_layout.setVerticalSpacing(0)

        # 创建日期按钮网格
        self.date_buttons = []
        for row in range(6):
            for col in range(7):
                btn = DateButton(self)
                calendar_layout.addWidget(btn, row, col)
                self.date_buttons.append(btn)

        main_layout.addWidget(calendar_frame)
        self.update_calendar()

    def update_calendar(self):
        # 断开之前的所有信号连接
        for btn in self.date_buttons:
            try:
                btn.clicked.disconnect()
            except:
                pass
            # 重置按钮状态
            btn.setText("")
            btn.setVisible(False)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-radius: 15px;
                    background: transparent;
                }
                QPushButton:hover {
                    background: #D3D3D3;
                }
                QPushButton:pressed {
                    background: #A9A9A9;
                }
            """)

        # 获取当月日历
        cal = calendar.monthcalendar(self.year, self.month)

        # 获取今天的日期
        today = datetime.now()
        today_str = f"{today.year}-{today.month:02d}-{today.day:02d}"

        # 更新按钮显示
        btn_idx = 0
        for week in cal:
            for day in week:
                btn = self.date_buttons[btn_idx]
                if day != 0:
                    btn.setText(str(day))
                    btn.setVisible(True)
                    btn.clicked.connect(lambda checked, d=day: self.on_date_click(d))

                    # 检查是否是今天的日期
                    current_date = f"{self.year}-{self.month:02d}-{day:02d}"
                    if current_date == today_str:
                        btn.set_today()
                    elif current_date in self.special_dates:
                        btn.setStyleSheet("""
                            QPushButton {
                                border: none;
                                border-radius: 17px;
                                background: #D3D3D3;
                            }
                        """)
                    else:
                        btn.setStyleSheet("""
                            QPushButton {
                                border: none;
                                border-radius: 17px;
                                background: transparent;
                            }
                            QPushButton:hover {
                                background: #D3D3D3;
                            }
                            QPushButton:pressed {
                                background: #A9A9A9;
                            }
                        """)
                btn_idx += 1

    def on_year_changed(self, year):
        self.year = int(year)
        self.update_calendar()

    def on_month_changed(self, month):
        self.month = int(month)
        self.update_calendar()

    def prev_month(self):
        if self.month > 1:
            self.month -= 1
        else:
            self.year -= 1
            self.month = 12
        self.year_combo.setCurrentText(str(self.year))
        self.month_combo.setCurrentText(str(self.month))
        self.update_calendar()

    def next_month(self):
        if self.month < 12:
            self.month += 1
        else:
            self.year += 1
            self.month = 1
        self.year_combo.setCurrentText(str(self.year))
        self.month_combo.setCurrentText(str(self.month))
        self.update_calendar()

    def on_date_click(self, day):
        if self.on_date_selected:
            self.on_date_selected(self.year, self.month, day)
            self.close()


class DateButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(35, 35)
        self.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 17px;
                background: transparent;
            }
            QPushButton:hover {
                background: #D3D3D3;
            }
            QPushButton:pressed {
                background: #A9A9A9;
            }
        """)

    def set_today(self):
        # 为今天的日期设置特殊样式：透明背景，黑色边框
        self.setStyleSheet("""
            QPushButton {
                border: 3px solid #DEE0E3;  /* 黑色边框 */
                border-radius: 17px;
                background: transparent;   /* 透明背景 */
                color: black;             /* 保持文字颜色为黑色 */
            }
            QPushButton:hover {
                background: #D3D3D3;
            }
            QPushButton:pressed {
                background: #A9A9A9;
            }
        """)


def show_calendar(parent=None, on_date_selected=None, special_dates=None):
    calendar = Calendar(parent, on_date_selected, special_dates)

    if parent:
        if parent.weizhi == 0:
            # 获取按钮的位置
            button = parent.date_edit_button
            button_pos = button.mapToGlobal(button.rect().bottomLeft())
            # 将日历窗口放在按钮正下方
            calendar.move(button_pos.x()-255, button_pos.y())
        else :
            # 获取按钮的位置
            button = parent.finishContent
            button_pos = button.mapToGlobal(button.rect().bottomLeft())
            # 将日历窗口放在按钮正下方
            calendar.move(button_pos.x() , button_pos.y())

    calendar.show()
    return calendar
