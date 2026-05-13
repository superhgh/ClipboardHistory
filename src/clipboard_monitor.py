"""
剪贴板监听模块 - 定时轮询方式，兼容所有 Windows 图片格式
"""

import hashlib
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QBuffer, QIODevice
from PyQt5.QtGui import QImage, QPixmap


class ClipboardMonitor(QObject):
    """剪贴板监听器（500ms 定时轮询）"""

    text_received = pyqtSignal(str)
    image_received = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._clipboard = QApplication.clipboard()
        self._last_hash = ""
        self._enabled = True
        self._suppress_next = False

        self._timer = QTimer(self)
        self._timer.setInterval(500)
        self._timer.timeout.connect(self._poll)

    def start(self):
        self._timer.start()

    def stop(self):
        self._timer.stop()

    def set_enabled(self, enabled):
        self._enabled = enabled

    def skip_next_change(self):
        """通知监听器忽略下一次变化"""
        self._suppress_next = True

    def _poll(self):
        """定时检查剪贴板内容（外层捕获异常防止定时器静默死亡）"""
        try:
            self._do_poll()
        except Exception:
            import traceback
            traceback.print_exc()

    def _do_poll(self):
        if not self._enabled:
            return

        if self._suppress_next:
            self._suppress_next = False
            self._last_hash = self._compute_clipboard_hash()
            return

        current_hash = self._compute_clipboard_hash()
        if not current_hash or current_hash == self._last_hash:
            return

        self._last_hash = current_hash

        # 先尝试图片
        image = self._get_image_from_clipboard()
        if image and not image.isNull():
            self.image_received.emit(image)
            return

        # 再尝试文字
        text = self._clipboard.text()
        if text and text.strip():
            self.text_received.emit(text)

    @staticmethod
    def _hash_image(qimage):
        """对 QImage 内容做 MD5，保证同一图片 hash 一致"""
        buf = QBuffer()
        buf.open(QIODevice.ReadWrite)
        qimage.save(buf, 'PNG')
        return hashlib.md5(buf.data()).hexdigest()

    def _compute_clipboard_hash(self):
        """计算当前剪贴板内容的稳定哈希值"""
        # 先尝试获取图片并计算内容 hash
        img = self._clipboard.image()
        if img and not img.isNull():
            return f"img:{self._hash_image(img)}"

        pix = self._clipboard.pixmap()
        if pix and not pix.isNull():
            return f"img:{self._hash_image(pix.toImage())}"

        # 文字
        text = self._clipboard.text()
        if text:
            return f"txt:{hashlib.md5(text.encode('utf-8', errors='ignore')).hexdigest()}"

        # HTML
        html = self._clipboard.mimeData().html()
        if html:
            return f"html:{hashlib.md5(html.encode('utf-8', errors='ignore')).hexdigest()}"

        # 文件 URL
        mime = self._clipboard.mimeData()
        if mime.hasUrls():
            urls = [u.toLocalFile() for u in mime.urls()]
            return f"urls:{hashlib.md5(str(urls).encode()).hexdigest()}"

        return ""

    def _get_image_from_clipboard(self):
        """多途径尝试从剪贴板获取图片"""
        img = self._clipboard.image()
        if img and not img.isNull():
            return img

        pix = self._clipboard.pixmap()
        if pix and not pix.isNull():
            return pix.toImage()

        mime = self._clipboard.mimeData()
        html = mime.html()
        if html and '<img' in html:
            import re
            try:
                src_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html)
                if src_match:
                    src = src_match.group(1)
                    if not src.startswith('http'):
                        img = QImage(src)
                        if not img.isNull():
                            return img
            except Exception:
                pass  # HTML 解析失败，继续尝试其他方式

        if mime.hasUrls():
            for url in mime.urls():
                try:
                    path = url.toLocalFile()
                    if path:
                        img = QImage(path)
                        if not img.isNull():
                            return img
                except Exception:
                    continue

        return None
