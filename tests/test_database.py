"""
database.py 单元测试
"""

import os
import tempfile
import pytest
from datetime import datetime, timedelta
import sqlite3

# 将 src 加入 path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import Database


@pytest.fixture
def db():
    """创建临时数据库用于测试"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    db = Database(db_path=path)
    yield db
    os.remove(path)


class TestDatabaseInit:
    def test_tables_created(self, db):
        """验证建表成功"""
        conn = db._get_conn()
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        conn.close()
        table_names = [t[0] for t in tables]
        assert 'clipboard_items' in table_names

    def test_connection_failure(self):
        """验证无效磁盘路径抛出 RuntimeError"""
        with pytest.raises(RuntimeError, match='无法创建数据库目录'):
            Database(db_path='Z:/不存在的磁盘/clipboard.db')


class TestAddItem:
    def test_add_text_item(self, db):
        """添加文字记录"""
        item_id = db.add_item('text', text_content='测试文字')
        assert item_id == 1

        item = db.get_item_by_id(item_id)
        assert item['content_type'] == 'text'
        assert item['text_content'] == '测试文字'
        assert item['image_path'] is None

    def test_add_image_item(self, db):
        """添加图片记录"""
        item_id = db.add_item('image', image_path='/data/img/1.png',
                              thumbnail_path='/data/thumb/1.png')
        item = db.get_item_by_id(item_id)
        assert item['content_type'] == 'image'
        assert item['image_path'] == '/data/img/1.png'
        assert item['thumbnail_path'] == '/data/thumb/1.png'

    def test_auto_timestamp(self, db):
        """验证自动生成时间戳"""
        item_id = db.add_item('text', text_content='时间戳测试')
        item = db.get_item_by_id(item_id)
        assert item['created_at'] is not None
        # 时间字符串格式: YYYY-MM-DD HH:MM:SS
        assert len(item['created_at']) >= 19


class TestDeleteItem:
    def test_delete_existing(self, db):
        """删除存在的记录"""
        item_id = db.add_item('text', text_content='待删除')
        db.delete_item(item_id)
        assert db.get_item_by_id(item_id) is None

    def test_delete_nonexistent(self, db):
        """删除不存在的记录不应报错"""
        db.delete_item(99999)


class TestDeleteExpired:
    def test_delete_expired_records(self, db):
        """清理过期记录"""
        # 手动插入一条过期的旧记录
        old_time = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
        conn = db._get_conn()
        conn.execute(
            "INSERT INTO clipboard_items (content_type, text_content, created_at) VALUES (?, ?, ?)",
            ('text', '旧记录', old_time)
        )
        conn.commit()
        conn.close()

        # 添加一条新记录
        db.add_item('text', text_content='新记录')

        affected = db.delete_expired(retention_days=3)
        assert affected >= 1

        items = db.get_all_items()
        assert all(i['text_content'] != '旧记录' for i in items)
        assert any(i['text_content'] == '新记录' for i in items)

    def test_pinned_not_deleted(self, db):
        """置顶记录不被清理"""
        old_time = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
        conn = db._get_conn()
        conn.execute(
            "INSERT INTO clipboard_items (content_type, text_content, created_at, is_pinned) VALUES (?, ?, ?, 1)",
            ('text', '置顶旧记录', old_time)
        )
        conn.commit()
        conn.close()

        affected = db.delete_expired(retention_days=3)
        assert affected == 0  # 置顶记录不删除

        items = db.get_all_items()
        assert any(i['text_content'] == '置顶旧记录' for i in items)


class TestTogglePin:
    def test_toggle_pin_on_off(self, db):
        """置顶状态切换"""
        item_id = db.add_item('text', text_content='切换置顶')
        db.toggle_pin(item_id)
        assert db.get_item_by_id(item_id)['is_pinned'] == 1

        db.toggle_pin(item_id)
        assert db.get_item_by_id(item_id)['is_pinned'] == 0


class TestMarkExpired:
    def test_mark_expired(self, db):
        """过期标记"""
        old_time = (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S')
        conn = db._get_conn()
        conn.execute(
            "INSERT INTO clipboard_items (content_type, text_content, created_at) VALUES (?, ?, ?)",
            ('text', '过期标记测试', old_time)
        )
        conn.commit()
        conn.close()

        affected = db.mark_expired(retention_days=3)
        assert affected >= 1

        items = db.get_all_items()
        old_item = next(i for i in items if i['text_content'] == '过期标记测试')
        assert old_item['is_expired'] == 1


class TestSearch:
    def test_search_finds_match(self, db):
        """搜索匹配文字"""
        db.add_item('text', text_content='今天天气真好')
        db.add_item('text', text_content='明天可能要下雨')
        db.add_item('text', text_content='后天去哪玩')

        results = db.search_items('天气')
        assert len(results) == 1
        assert '天气' in results[0]['text_content']

    def test_search_no_match(self, db):
        """搜索无匹配"""
        db.add_item('text', text_content='hello world')
        results = db.search_items('不存在的关键词')
        assert len(results) == 0

    def test_search_only_text(self, db):
        """搜索仅匹配文字，不含图片"""
        db.add_item('text', text_content='test')
        db.add_item('image', image_path='/img/test.png')

        results = db.search_items('test')
        assert len(results) == 1
        assert results[0]['content_type'] == 'text'


class TestGetAllItems:
    def test_order_by_pinned_and_time(self, db):
        """验证排序：置顶优先，然后时间倒序"""
        db.add_item('text', text_content='first')
        db.add_item('text', text_content='second')
        db.add_item('text', text_content='third')

        # 置顶第二条
        db.toggle_pin(2)

        items = db.get_all_items()
        assert items[0]['id'] == 2  # 置顶的排第一
        assert items[0]['is_pinned'] == 1

    def test_empty_database(self, db):
        """空数据库返回空列表"""
        items = db.get_all_items()
        assert items == []
