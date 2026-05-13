"""
data_manager.py 单元测试
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_manager import DataManager
from src.database import Database


@pytest.fixture
def dm():
    """创建使用临时数据库的 DataManager"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    dm = DataManager()
    dm.db = Database(db_path=path)

    yield dm

    os.remove(path)


class TestTextOperations:
    def test_add_text(self, dm):
        """添加文字记录"""
        item_id = dm.add_text('Hello World')
        assert item_id is not None
        item = dm.get_item_by_id(item_id)
        assert item['content_type'] == 'text'
        assert item['text_content'] == 'Hello World'

    def test_add_text_dedup(self, dm):
        """重复文字不应重复记录"""
        first = dm.add_text('相同内容')
        assert first is not None
        second = dm.add_text('相同内容')
        assert second is None  # 去重

    def test_add_text_different(self, dm):
        """不同文字分别记录"""
        first = dm.add_text('内容A')
        second = dm.add_text('内容B')
        assert first is not None
        assert second is not None
        assert first != second

    def test_add_text_after_image(self, dm):
        """文字在图片之后不会被误判为重复"""
        # 模拟数据库中有图片记录
        dm.db.add_item('image', image_path='/img/test.png')
        item_id = dm.add_text('新文字')
        assert item_id is not None


class TestImageOperations:
    def test_add_image_md5_dedup(self, dm):
        """验证图片用 MD5 去重"""
        from PyQt5.QtGui import QImage
        # 创建两个相同内容的 QImage
        img1 = QImage(100, 100, QImage.Format_ARGB32)
        img1.fill(0xFF0000)
        img2 = QImage(100, 100, QImage.Format_ARGB32)
        img2.fill(0xFF0000)

        id1 = dm.add_image(img1)
        assert id1 is not None

        id2 = dm.add_image(img2)
        assert id2 is None  # 相同图片去重

    def test_add_different_images(self, dm):
        """不同图片分别存储"""
        from PyQt5.QtGui import QImage
        img1 = QImage(100, 100, QImage.Format_ARGB32)
        img1.fill(0xFF0000)
        img2 = QImage(100, 100, QImage.Format_ARGB32)
        img2.fill(0x00FF00)

        id1 = dm.add_image(img1)
        id2 = dm.add_image(img2)
        assert id1 is not None
        assert id2 is not None
        assert id1 != id2


class TestExpiry:
    def test_clean_expired(self, dm):
        """清理过期记录"""
        import sqlite3
        from datetime import datetime, timedelta

        # 手动插入过期记录
        old_time = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
        conn = dm.db._get_conn()
        conn.execute(
            "INSERT INTO clipboard_items (content_type, text_content, created_at) VALUES (?, ?, ?)",
            ('text', '过期数据', old_time)
        )
        conn.commit()
        conn.close()

        dm.set_retention_days(3)
        count = dm.clean_expired()
        assert count >= 1

    def test_retention_days_default(self, dm):
        """默认存储期限为 3 天"""
        assert dm.get_retention_days() == 3

    def test_set_retention_days(self, dm):
        """切换存储期限"""
        dm.set_retention_days(5)
        assert dm.get_retention_days() == 5

        dm.set_retention_days(1)
        assert dm.get_retention_days() == 1


class TestItemManagement:
    def test_delete_item(self, dm):
        """删除记录"""
        item_id = dm.add_text('待删除')
        dm.delete_item(item_id)
        assert dm.get_item_by_id(item_id) is None

    def test_toggle_pin(self, dm):
        """切换置顶"""
        item_id = dm.add_text('切换置顶测试')
        dm.toggle_pin(item_id)
        assert dm.get_item_by_id(item_id)['is_pinned'] == 1
        dm.toggle_pin(item_id)
        assert dm.get_item_by_id(item_id)['is_pinned'] == 0

    def test_search(self, dm):
        """搜索"""
        dm.add_text('Python编程')
        dm.add_text('Java开发')
        dm.add_text('Python数据分析')

        results = dm.search_items('Python')
        assert len(results) == 2


class TestDeleteItemFiles:
    def test_delete_item_removes_image_files(self, dm):
        """删除图片记录时同时删除文件"""
        import tempfile
        # 创建临时图片文件
        fd, img_path = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        fd, thumb_path = tempfile.mkstemp(suffix='.png')
        os.close(fd)

        item_id = dm.db.add_item('image', image_path=img_path, thumbnail_path=thumb_path)
        assert os.path.exists(img_path)
        assert os.path.exists(thumb_path)

        dm.delete_item(item_id)
        assert not os.path.exists(img_path)
        assert not os.path.exists(thumb_path)
