from PyQt6.QtWidgets import (QWidget, QLabel, QComboBox, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QGridLayout)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QPixmap, QPainter
from datetime import datetime
import calendar
import os

class Calendar(QWidget):
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
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # 设置背景图片
        self.bg_image = QPixmap(self.normalized_path + '/includes/Icons/general/lsbj.png')
        
        # 初始化日期
        self.current_date = QDate.currentDate()
        self.year = self.current_date.year()
        self.month = self.current_date.month()
        
        # 创建布局
        self.create_calendar()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.bg_image)
        
    def create_calendar(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(0)  # 减少垂直间距
        
        # 年月选择部分
        date_frame = QWidget()
        date_frame.setFixedHeight(35)  # 固定高度
        date_layout = QHBoxLayout(date_frame)
        date_layout.setContentsMargins(0, 0, 0, 0)
        
        # 定义统一的样式
        combo_style = """
            QComboBox {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                background: white;
            }
            QComboBox::drop-down {
                border-left: 1px solid #CCCCCC;
                background: white;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                background-Image: url("C:\py\pythonProject\.venv\down-arrow.png);    
            }
            QComboBox QAbstractItemView {
                background: white;
                selection-background-color: #D3D3D3;
                border: 1px solid #CCCCCC;
            }
            QComboBox QAbstractItemView::item {
                height: 25px;
                padding-left: 5px;
                background-color: #F5F5F5;  /* 浅灰色背景 */
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #a0c8ff;  /* Hover color */
                color: white;  /* Text color when hovered */
            }
            
        """
        
        # 年份选择
        self.year_combo = QComboBox()
        self.year_combo.addItems([str(year) for year in range(self.year - 10, self.year + 11)])
        self.year_combo.setCurrentText(str(self.year))
        self.year_combo.currentTextChanged.connect(self.on_year_changed)
        self.year_combo.setFixedWidth(80)
        self.year_combo.setStyleSheet(combo_style)
        
        # 月份选择
        self.month_combo = QComboBox()
        self.month_combo.addItems([str(month) for month in range(1, 13)])
        self.month_combo.setCurrentText(str(self.month))
        self.month_combo.currentTextChanged.connect(self.on_month_changed)
        self.month_combo.setFixedWidth(60)
        self.month_combo.setStyleSheet(combo_style)
        
        date_layout.addWidget(self.year_combo)
        date_layout.addWidget(QLabel("年"))
        date_layout.addWidget(self.month_combo)
        date_layout.addWidget(QLabel("月"))
        date_layout.addStretch()
        
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
        calendar_layout.setSpacing(0)
        
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
        
        # 更新按钮显示
        btn_idx = 0
        for week in cal:
            for day in week:
                btn = self.date_buttons[btn_idx]
                if day != 0:
                    btn.setText(str(day))
                    btn.setVisible(True)
                    btn.clicked.connect(lambda checked, d=day: self.on_date_click(d))
                    
                    # 检查是否是特殊日期
                    date_str = f"{self.year}-{self.month:02d}-{day:02d}"
                    if date_str in self.special_dates:
                        btn.setStyleSheet("""
                            QPushButton {
                                border: none;
                                border-radius: 15px;
                                background: #393939;
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
        self.setFixedSize(30, 30)
        self.setStyleSheet("""
            QPushButton {
                border: 1px solid #D3D3D3;
                border-radius: 15px;
                background: transparent;
            }
            QPushButton:hover {
                background: #D3D3D3;
                border-radius: 15px;
            }
            QPushButton:pressed {
                background: #A9A9A9;
                border-radius: 15px;
            }
        """)

def show_calendar(parent=None, on_date_selected=None, special_dates=None):
    calendar = Calendar(parent, on_date_selected, special_dates)
    
    if parent:
        # 获取按钮的位置
        button = parent.date_edit_button
        button_pos = button.mapToGlobal(button.rect().bottomLeft())
        # 将日历窗口放在按钮正下方
        calendar.move(button_pos.x()-255, button_pos.y())
    
    calendar.show()
    return calendar
