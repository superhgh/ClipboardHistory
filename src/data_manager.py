"""
数据管理器模块 - 业务逻辑层
"""

import os
from datetime import datetime
from src.database import Database
from src.image_utils import save_image_from_qimage
from PyQt5.QtGui import QImage


class DataManager:
    """协调数据库和业务逻辑"""

    def __init__(self):
        from src.paths import get_db_path
        self.db = Database(get_db_path())
        self._retention_days = 3
        self._last_image_hash = None

    def set_retention_days(self, days):
        """设置存储期限"""
        self._retention_days = days
        self._update_expired_flags()

    def get_retention_days(self):
        return self._retention_days

    def _update_expired_flags(self):
        """根据当前期限更新过期标记"""
        self.db.clear_expired_flag()
        self.db.mark_expired(self._retention_days)

    def add_text(self, text):
        """添加文字记录，自动去重"""
        try:
            items = self.db.get_all_items()
            if items:
                last = items[0]
                if last['content_type'] == 'text' and last['text_content'] == text:
                    return None
        except Exception as e:
            raise RuntimeError(f"查询最后一条记录失败: {e}") from e

        try:
            item_id = self.db.add_item('text', text_content=text)
        except Exception as e:
            raise RuntimeError(f"文字记录入库失败: {e}") from e

        self._update_expired_flags()
        return item_id

    def add_image(self, qimage):
        """添加图片记录，通过 MD5 内容去重"""
        import hashlib
        from PyQt5.QtCore import QBuffer, QIODevice

        # 计算图片内容 MD5
        buf = QBuffer()
        buf.open(QIODevice.ReadWrite)
        qimage.save(buf, 'PNG')
        img_hash = hashlib.md5(buf.data()).hexdigest()

        # 与上一条图片记录比较，去重
        if self._last_image_hash == img_hash:
            return None
        self._last_image_hash = img_hash

        # 先存图片文件，再入库（避免入库后存图失败产生脏记录）
        try:
            from src.paths import get_images_dir, get_thumbnails_dir
            temp_id = img_hash[:8]  # 临时用 hash 前 8 位做文件名
            image_path, thumb_path = save_image_from_qimage(qimage, temp_id)
        except Exception as e:
            raise RuntimeError(f"图片保存失败: {e}") from e

        try:
            item_id = self.db.add_item('image', image_path=image_path, thumbnail_path=thumb_path)
        except Exception as e:
            # 入库失败则删除已保存的文件
            for p in (image_path, thumb_path):
                if p and os.path.exists(p):
                    try:
                        os.remove(p)
                    except OSError:
                        pass
            raise RuntimeError(f"图片记录入库失败: {e}") from e

        self._update_expired_flags()
        return item_id

    def delete_item(self, item_id):
        """删除记录及相关文件"""
        item = self.db.get_item_by_id(item_id)
        if item:
            # 删除图片文件
            if item['image_path'] and os.path.exists(item['image_path']):
                try:
                    os.remove(item['image_path'])
                except OSError:
                    pass
            if item['thumbnail_path'] and os.path.exists(item['thumbnail_path']):
                try:
                    os.remove(item['thumbnail_path'])
                except OSError:
                    pass
        self.db.delete_item(item_id)

    def toggle_pin(self, item_id):
        """切换置顶"""
        self.db.toggle_pin(item_id)

    def clean_expired(self):
        """清理所有过期记录"""
        affected = self.db.delete_expired(self._retention_days)
        return affected

    def get_all_items(self):
        """获取所有记录"""
        self._update_expired_flags()
        return self.db.get_all_items()

    def search_items(self, keyword):
        """搜索文字记录"""
        return self.db.search_items(keyword)

    def get_item_by_id(self, item_id):
        return self.db.get_item_by_id(item_id)
