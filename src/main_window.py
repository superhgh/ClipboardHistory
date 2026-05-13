"""
主窗口模块 - 应用主界面
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QLabel, QScrollArea, QPushButton,
                             QRadioButton, QButtonGroup, QMessageBox, QApplication,
                             QCheckBox)
from PyQt5.QtCore import Qt, QTimer

from src.card_widget import TextCard, ImageCard
from src.data_manager import DataManager
from src.clipboard_monitor import ClipboardMonitor
from src.styles import build_qss


class MainWindow(QMainWindow):
    FONT_MIN = 20
    FONT_MAX = 50

    def __init__(self):
        super().__init__()
        self.setWindowTitle('历史粘贴板')
        self.resize(800, 900)
        self.setMinimumSize(600, 700)

        self._font_size = 24
        self.data_manager = DataManager()
        self.clipboard_monitor = ClipboardMonitor()

        self._selected_ids = set()

        self._setup_ui()
        self._apply_style()
        self._connect_signals()
        self._load_items()

        self.clipboard_monitor.start()

    # ===== 样式 =====

    def _apply_style(self):
        self.setStyleSheet(build_qss(self._font_size))

    def _on_font_increase(self):
        if self._font_size < self.FONT_MAX:
            self._font_size += 2
            self._apply_style()
            self._update_font_label()

    def _on_font_decrease(self):
        if self._font_size > self.FONT_MIN:
            self._font_size -= 2
            self._apply_style()
            self._update_font_label()

    def _update_font_label(self):
        self.font_size_label.setText(str(self._font_size))

    # ===== UI 搭建 =====

    def _setup_ui(self):
        central = QWidget()
        central.setObjectName('centralWidget')
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===== 顶部区域 =====
        header = QWidget()
        header.setObjectName('headerWidget')
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 12)
        header_layout.setSpacing(12)

        # 标题 + 搜索框
        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)

        title = QLabel('📋 历史粘贴板')
        title.setStyleSheet('font-size: 36px; font-weight: bold; color: #333333;')
        search_layout.addWidget(title)

        search_layout.addStretch()

        self.search_edit = QLineEdit()
        self.search_edit.setObjectName('searchEdit')
        self.search_edit.setPlaceholderText('搜索复制内容...')
        self.search_edit.setClearButtonEnabled(True)
        search_layout.addWidget(self.search_edit, 1)

        header_layout.addLayout(search_layout)

        # 存储期限 + 字体调节
        settings_layout = QHBoxLayout()
        settings_layout.setSpacing(16)

        # 存储期限
        expiry_label = QLabel('存储期限:')
        expiry_label.setObjectName('expiryLabel')
        settings_layout.addWidget(expiry_label)

        self.expiry_group = QButtonGroup(self)
        self.expiry_btns = {}
        for days, label in [(1, '1天'), (3, '3天'), (5, '5天')]:
            rb = QRadioButton(label)
            if days == self.data_manager.get_retention_days():
                rb.setChecked(True)
            self.expiry_group.addButton(rb, days)
            self.expiry_btns[days] = rb
            settings_layout.addWidget(rb)

        settings_layout.addSpacing(30)

        # 字体大小调节
        font_label = QLabel('字体:')
        font_label.setObjectName('expiryLabel')
        settings_layout.addWidget(font_label)

        self.font_minus_btn = QPushButton('A-')
        self.font_minus_btn.setObjectName('fontBtn')
        settings_layout.addWidget(self.font_minus_btn)

        self.font_size_label = QLabel(str(self._font_size))
        self.font_size_label.setObjectName('fontSizeLabel')
        self.font_size_label.setAlignment(Qt.AlignCenter)
        settings_layout.addWidget(self.font_size_label)

        self.font_plus_btn = QPushButton('A+')
        self.font_plus_btn.setObjectName('fontBtn')
        settings_layout.addWidget(self.font_plus_btn)

        settings_layout.addStretch()
        header_layout.addLayout(settings_layout)

        main_layout.addWidget(header)

        # ===== 多选工具栏 =====
        select_bar = QWidget()
        select_bar_layout = QHBoxLayout(select_bar)
        select_bar_layout.setContentsMargins(20, 8, 20, 4)
        select_bar_layout.setSpacing(12)

        self.select_all_btn = QPushButton('☑ 全选')
        self.select_all_btn.setObjectName('copyBtn')
        select_bar_layout.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton('☐ 取消全选')
        self.deselect_all_btn.setObjectName('pinBtn')
        select_bar_layout.addWidget(self.deselect_all_btn)

        self.delete_selected_btn = QPushButton('🗑 删除选中')
        self.delete_selected_btn.setObjectName('dangerBtn')
        select_bar_layout.addWidget(self.delete_selected_btn)

        self.selected_count_label = QLabel('未选中')
        self.selected_count_label.setStyleSheet(
            f'font-size: {self._font_size - 4}px; color: #999999;'
        )
        select_bar_layout.addWidget(self.selected_count_label)

        select_bar_layout.addStretch()

        main_layout.addWidget(select_bar)

        # ===== 卡片列表区域 =====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.card_container = QWidget()
        self.card_container.setObjectName('cardContainer')
        self.card_layout = QVBoxLayout(self.card_container)
        self.card_layout.setContentsMargins(20, 12, 20, 12)
        self.card_layout.setSpacing(16)
        self.card_layout.addStretch()

        scroll.setWidget(self.card_container)
        main_layout.addWidget(scroll, 1)

        # ===== 底部区域 =====
        bottom = QWidget()
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(20, 12, 20, 16)
        bottom_layout.setSpacing(16)

        # 复制反馈区域
        self.copy_toast = QLabel('')
        self.copy_toast.setObjectName('copyToast')
        bottom_layout.addWidget(self.copy_toast)

        # 状态 + 记录数
        self.status_label = QLabel()
        self.status_label.setObjectName('statusLabel')
        bottom_layout.addWidget(self.status_label)

        bottom_layout.addStretch()

        self.delete_all_btn = QPushButton('🗑 删除全部')
        self.delete_all_btn.setObjectName('bottomBtn')
        self.delete_all_btn.setStyleSheet(
            'QPushButton#bottomBtn { background-color: #FF4444; color: #FFFFFF; }'
            'QPushButton#bottomBtn:hover { background-color: #DD0000; }'
        )
        bottom_layout.addWidget(self.delete_all_btn)

        self.clean_btn = QPushButton('🧹 清理过期')
        self.clean_btn.setObjectName('bottomBtn')
        bottom_layout.addWidget(self.clean_btn)

        main_layout.addWidget(bottom)

        # 反馈计时器
        self._toast_timer = QTimer(self)
        self._toast_timer.setSingleShot(True)
        self._toast_timer.timeout.connect(self._clear_toast)

    # ===== 信号连接 =====

    def _connect_signals(self):
        self.search_edit.textChanged.connect(self._on_search)
        self.expiry_group.buttonClicked.connect(self._on_expiry_changed)
        self.clean_btn.clicked.connect(self._on_clean_expired)
        self.delete_all_btn.clicked.connect(self._on_delete_all)

        self.select_all_btn.clicked.connect(self._on_select_all)
        self.deselect_all_btn.clicked.connect(self._on_deselect_all)
        self.delete_selected_btn.clicked.connect(self._on_delete_selected)

        self.font_plus_btn.clicked.connect(self._on_font_increase)
        self.font_minus_btn.clicked.connect(self._on_font_decrease)

        self.clipboard_monitor.text_received.connect(self._on_text_copied)
        self.clipboard_monitor.image_received.connect(self._on_image_copied)

    # ===== 复制反馈 =====

    def _show_copy_toast(self):
        self.copy_toast.setStyleSheet('')  # 重置为 QSS 定义的样式
        self.copy_toast.setText('✅ 已复制到剪贴板!')
        self._toast_timer.start(2000)

    def _clear_toast(self):
        self.copy_toast.setStyleSheet('')
        self.copy_toast.setText('')

    def _show_error(self, msg):
        """在底部状态栏显示错误信息"""
        self.copy_toast.setStyleSheet(
            f'font-size: {self._font_size - 4}px; color: #FF4444; font-weight: bold; padding: 8px 20px;'
        )
        self.copy_toast.setText(f'❌ {msg}')
        self._toast_timer.start(4000)  # 错误信息显示更长

    # ===== 数据加载 =====

    def _load_items(self):
        self._clear_cards()
        items = self.data_manager.get_all_items()
        self._render_items(items)
        self._update_selected_count()

    def _render_items(self, items):
        if self.card_layout.count() > 0:
            item = self.card_layout.takeAt(self.card_layout.count() - 1)
            if item:
                del item

        self._card_widgets = {}

        if not items:
            empty = QLabel('暂无复制记录\n复制文字或图片后，内容将显示在这里')
            empty.setObjectName('emptyLabel')
            empty.setAlignment(Qt.AlignCenter)
            self.card_layout.addWidget(empty)
            self.status_label.setText('0 条记录')
            return

        for item_data in items:
            if item_data['content_type'] == 'text':
                card = TextCard(item_data)
            else:
                card = ImageCard(item_data)

            card.copy_requested.connect(self._on_copy_item)
            card.pin_requested.connect(self._on_toggle_pin)
            card.delete_requested.connect(self._on_delete_item)
            card.selected_changed.connect(self._on_item_selected)
            card.content_clicked.connect(self._on_content_clicked)

            if item_data['id'] in self._selected_ids:
                card.set_checked(True)

            self.card_layout.addWidget(card)
            self._card_widgets[item_data['id']] = card

        self.card_layout.addStretch()
        self.status_label.setText(f'{len(items)} 条记录')

    def _clear_cards(self):
        while self.card_layout.count() > 0:
            item = self.card_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self._card_widgets = {}

    # ===== 搜索 =====

    def _on_search(self, keyword):
        self._clear_cards()
        if not keyword.strip():
            items = self.data_manager.get_all_items()
        else:
            items = self.data_manager.search_items(keyword.strip())
        self._render_items(items)
        self._update_selected_count()

    # ===== 存储期限 =====

    def _on_expiry_changed(self, button):
        days = self.expiry_group.id(button)
        self.data_manager.set_retention_days(days)
        self._load_items()

    def _on_clean_expired(self):
        count = self.data_manager.clean_expired()
        if count > 0:
            self._load_items()
            QMessageBox.information(self, '清理完成', f'已清理 {count} 条过期记录')
        else:
            QMessageBox.information(self, '无需清理', '没有过期记录需要清理')

    # ===== 删除全部 =====

    def _on_delete_all(self):
        items = self.data_manager.get_all_items()
        if not items:
            QMessageBox.information(self, '无记录', '没有可删除的记录')
            return
        reply = QMessageBox.question(
            self, '确认删除全部',
            f'确定要删除全部 {len(items)} 条记录吗？\n此操作不可恢复！',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for item in items:
                self.data_manager.delete_item(item['id'])
            self._selected_ids.clear()
            self._load_items()

    # ===== 多选功能 =====

    def _on_item_selected(self, item_id, checked):
        if checked:
            self._selected_ids.add(item_id)
        else:
            self._selected_ids.discard(item_id)
        self._update_selected_count()

    def _on_select_all(self):
        self._selected_ids.clear()
        for item_id in self._card_widgets:
            self._selected_ids.add(item_id)
            self._card_widgets[item_id].set_checked(True)
        self._update_selected_count()

    def _on_deselect_all(self):
        self._selected_ids.clear()
        for item_id in self._card_widgets:
            self._card_widgets[item_id].set_checked(False)
        self._update_selected_count()

    def _on_delete_selected(self):
        if not self._selected_ids:
            QMessageBox.information(self, '未选择', '请先勾选要删除的记录')
            return
        reply = QMessageBox.question(
            self, '确认删除',
            f'确定要删除选中的 {len(self._selected_ids)} 条记录吗？',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for item_id in list(self._selected_ids):
                self.data_manager.delete_item(item_id)
            self._selected_ids.clear()
            self._load_items()

    def _update_selected_count(self):
        total = len(self._card_widgets)
        selected = len(self._selected_ids)
        if selected > 0:
            self.selected_count_label.setText(f'已选 {selected}/{total}')
        else:
            self.selected_count_label.setText(f'共 {total} 条')

    # ===== 剪贴板回调 =====

    def _on_text_copied(self, text):
        if len(text) > 100000:
            text = text[:100000]
        try:
            result = self.data_manager.add_text(text)
            if result is not None:
                self._load_items()
        except Exception as e:
            self._show_error(f'保存文字失败: {e}')

    def _on_image_copied(self, qimage):
        try:
            result = self.data_manager.add_image(qimage)
            if result is not None:
                self._load_items()
        except Exception as e:
            self._show_error(f'保存图片失败: {e}')

    # ===== 卡片操作 =====

    def _on_content_clicked(self, item_id):
        """点击内容区域直接复制"""
        self._do_copy(item_id)

    def _on_copy_item(self, item_id):
        """点击复制按钮"""
        self._do_copy(item_id)

    def _do_copy(self, item_id):
        try:
            item = self.data_manager.get_item_by_id(item_id)
            if not item:
                return

            # 抑制剪贴板监听（避免软件自己触发的变化被记录）
            self.clipboard_monitor.skip_next_change()

            clipboard = QApplication.clipboard()
            if item['content_type'] == 'text':
                clipboard.setText(item['text_content'] or '')
            elif item['image_path']:
                import os
                from PyQt5.QtGui import QPixmap
                from PyQt5.QtCore import QUrl, QMimeData
                if not os.path.exists(item['image_path']):
                    self._show_error('图片文件不存在，可能已被移动或删除')
                    return
                pixmap = QPixmap(item['image_path'])
                if pixmap.isNull():
                    self._show_error('图片文件已损坏，无法读取')
                    return
                mime = QMimeData()
                mime.setImageData(pixmap.toImage())
                mime.setUrls([QUrl.fromLocalFile(
                    os.path.abspath(item['image_path'])
                )])
                clipboard.setMimeData(mime)

            # 卡片高亮闪烁
            if item_id in self._card_widgets:
                self._card_widgets[item_id].flash_highlight()

            # 显示复制成功反馈
            self._show_copy_toast()
        except Exception as e:
            self._show_error(f'复制失败: {e}')

    def _on_toggle_pin(self, item_id):
        self.data_manager.toggle_pin(item_id)
        self._load_items()

    def _on_delete_item(self, item_id):
        reply = QMessageBox.question(
            self, '确认删除', '确定要删除这条记录吗？',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.data_manager.delete_item(item_id)
            self._selected_ids.discard(item_id)
            self._load_items()

    def closeEvent(self, event):
        self.clipboard_monitor.stop()
        event.accept()
