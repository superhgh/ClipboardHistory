"""
卡片组件 - 文字卡片和图片卡片
"""

from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QCheckBox, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QEvent, QTimer
from PyQt5.QtGui import QPixmap


class ClickableLabel(QLabel):
    """支持点击事件的内容标签"""
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class CardBase(QFrame):
    """卡片基类"""

    copy_requested = pyqtSignal(int)
    pin_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    selected_changed = pyqtSignal(int, bool)  # item_id, checked
    content_clicked = pyqtSignal(int)  # 点击内容区域时触发

    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.item_id = item_data['id']
        self.setObjectName('cardFrame')
        self.setProperty('expired', str(item_data.get('is_expired', 0)) == '1')
        self.setProperty('pinned', str(item_data.get('is_pinned', 0)) == '1')
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # 顶部栏：复选框 + 时间 + 操作按钮
        top_layout = QHBoxLayout()
        top_layout.setSpacing(6)

        # 多选复选框
        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(
            lambda state: self.selected_changed.emit(
                self.item_id, state == Qt.Checked
            )
        )
        top_layout.addWidget(self.checkbox)

        # 置顶标记
        self.pin_indicator = QLabel()
        if self.item_data.get('is_pinned'):
            self.pin_indicator.setText('📌')
        else:
            self.pin_indicator.setText('')
        self.pin_indicator.setFixedWidth(30)
        top_layout.addWidget(self.pin_indicator)

        # 时间
        self.time_label = QLabel(self.item_data.get('created_at', ''))
        self.time_label.setObjectName('timeLabel')
        top_layout.addWidget(self.time_label)

        top_layout.addStretch()

        # 过期标记
        if self.item_data.get('is_expired'):
            expired_label = QLabel('已过期')
            expired_label.setStyleSheet('font-size: 24px; color: #FF6B6B;')
            top_layout.addWidget(expired_label)

        # 置顶按钮
        pin_text = '📌 取消置顶' if self.item_data.get('is_pinned') else '📌 置顶'
        self.pin_btn = QPushButton(pin_text)
        self.pin_btn.setObjectName('pinBtn')
        self.pin_btn.clicked.connect(lambda: self.pin_requested.emit(self.item_id))
        top_layout.addWidget(self.pin_btn)

        # 复制按钮
        self.copy_btn = QPushButton('📋 复制')
        self.copy_btn.setObjectName('copyBtn')
        self.copy_btn.clicked.connect(lambda: self.copy_requested.emit(self.item_id))
        top_layout.addWidget(self.copy_btn)

        # 删除按钮
        self.del_btn = QPushButton('🗑 删除')
        self.del_btn.setObjectName('dangerBtn')
        self.del_btn.clicked.connect(lambda: self.delete_requested.emit(self.item_id))
        top_layout.addWidget(self.del_btn)

        layout.addLayout(top_layout)
        self._add_content(layout)

    def _add_content(self, layout):
        raise NotImplementedError

    def set_checked(self, checked):
        self.checkbox.setChecked(checked)

    def flash_highlight(self):
        """复制成功时高亮闪烁卡片边框"""
        original = self.styleSheet()
        self.setStyleSheet(
            'QFrame#cardFrame {'
            '  border: 3px solid #4CAF50;'
            '  background-color: #F0FFF0;'
            '  border-radius: 12px;'
            '}'
        )
        QTimer.singleShot(600, lambda: self.setStyleSheet(original))


class TextCard(CardBase):
    """文字卡片"""

    def _add_content(self, layout):
        text = self.item_data.get('text_content', '')
        self.content_label = ClickableLabel(text)
        self.content_label.setObjectName('contentLabel')
        self.content_label.setWordWrap(True)
        self.content_label.setMaximumHeight(260)
        self.content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.content_label.clicked.connect(
            lambda: self.content_clicked.emit(self.item_id)
        )
        layout.addWidget(self.content_label)


class ImageCard(CardBase):
    """图片卡片"""

    def _add_content(self, layout):
        thumb_path = self.item_data.get('thumbnail_path', '')
        self.image_label = ClickableLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(120)

        if thumb_path:
            pixmap = QPixmap(thumb_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    260, 260, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled)

        self.image_label.clicked.connect(
            lambda: self.content_clicked.emit(self.item_id)
        )
        layout.addWidget(self.image_label)
