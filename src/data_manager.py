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
        self._retention_days = 3  # 默认3天
        self._next_image_id = self._get_next_id()

    def _get_next_id(self):
        """预估下一个可用 ID"""
        items = self.db.get_all_items()
        if items:
            return max(item['id'] for item in items) + 1
        return 1

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
        # 检查是否与最后一条文字记录相同
        items = self.db.get_all_items()
        if items:
            last = items[0]
            if last['content_type'] == 'text' and last['text_content'] == text:
                return None  # 重复内容，跳过

        item_id = self.db.add_item('text', text_content=text)
        self._update_expired_flags()
        return item_id

    def add_image(self, qimage):
        """添加图片记录，自动去重"""
        # 检查是否与最后一条图片记录相同（通过 hash）
        current_hash = qimage.cacheKey()
        items = self.db.get_all_items()
        if items:
            last = items[0]
            if last['content_type'] == 'image':
                # 简单去重：比较 cacheKey
                if hasattr(self, '_last_image_hash') and self._last_image_hash == current_hash:
                    return None

        self._last_image_hash = current_hash

        # 先创建记录，获取 id
        item_id = self.db.add_item('image')
        # 再保存图片文件
        try:
            image_path, thumb_path = save_image_from_qimage(qimage, item_id)
            # 更新记录中的路径
            conn = self.db._get_conn()
            conn.execute(
                "UPDATE clipboard_items SET image_path = ?, thumbnail_path = ? WHERE id = ?",
                (image_path, thumb_path, item_id)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            # 图片保存失败，删除记录
            self.db.delete_item(item_id)
            raise e

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
