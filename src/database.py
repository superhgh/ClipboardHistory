"""
数据库模块 - SQLite 数据存储
"""

import sqlite3
import os
from datetime import datetime, timedelta


class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            from src.paths import get_db_path
            db_path = get_db_path()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            return conn
        except sqlite3.Error as e:
            raise RuntimeError(f"数据库连接失败: {e}") from e

    def _init_db(self):
        conn = self._get_conn()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clipboard_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_type TEXT NOT NULL,
                    text_content TEXT,
                    image_path TEXT,
                    thumbnail_path TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                    is_pinned INTEGER NOT NULL DEFAULT 0,
                    is_expired INTEGER NOT NULL DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at ON clipboard_items(created_at DESC)
            """)
            conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"数据库初始化失败: {e}") from e
        finally:
            conn.close()

    def add_item(self, content_type, text_content=None, image_path=None, thumbnail_path=None):
        """添加一条记录，返回新记录的 id"""
        conn = self._get_conn()
        try:
            conn.execute(
                "INSERT INTO clipboard_items (content_type, text_content, image_path, thumbnail_path) VALUES (?, ?, ?, ?)",
                (content_type, text_content, image_path, thumbnail_path)
            )
            conn.commit()
            item_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            return item_id
        except sqlite3.Error as e:
            raise RuntimeError(f"添加记录失败: {e}") from e
        finally:
            conn.close()

    def delete_item(self, item_id):
        """删除单条记录"""
        conn = self._get_conn()
        try:
            conn.execute("DELETE FROM clipboard_items WHERE id = ?", (item_id,))
            conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"删除记录失败: {e}") from e
        finally:
            conn.close()

    def delete_expired(self, retention_days):
        """删除所有过期记录，返回删除数量"""
        cutoff = (datetime.now() - timedelta(days=retention_days)).strftime('%Y-%m-%d %H:%M:%S')
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "DELETE FROM clipboard_items WHERE created_at < ? AND is_pinned = 0",
                (cutoff,)
            )
            affected = cursor.rowcount
            conn.commit()
            return affected
        except sqlite3.Error as e:
            raise RuntimeError(f"清理过期记录失败: {e}") from e
        finally:
            conn.close()

    def toggle_pin(self, item_id):
        """切换置顶状态"""
        conn = self._get_conn()
        try:
            conn.execute(
                "UPDATE clipboard_items SET is_pinned = CASE WHEN is_pinned = 0 THEN 1 ELSE 0 END WHERE id = ?",
                (item_id,)
            )
            conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"置顶操作失败: {e}") from e
        finally:
            conn.close()

    def mark_expired(self, retention_days):
        """标记过期记录（不删除，仅标记），返回标记数量"""
        cutoff = (datetime.now() - timedelta(days=retention_days)).strftime('%Y-%m-%d %H:%M:%S')
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "UPDATE clipboard_items SET is_expired = 1 WHERE created_at < ? AND is_expired = 0 AND is_pinned = 0",
                (cutoff,)
            )
            affected = cursor.rowcount
            conn.commit()
            return affected
        except sqlite3.Error as e:
            raise RuntimeError(f"标记过期失败: {e}") from e
        finally:
            conn.close()

    def clear_expired_flag(self):
        """清除所有过期标记（切换存储期限后调用）"""
        conn = self._get_conn()
        try:
            conn.execute("UPDATE clipboard_items SET is_expired = 0 WHERE is_expired = 1")
            conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"清除过期标记失败: {e}") from e
        finally:
            conn.close()

    def get_all_items(self):
        """获取所有记录，按置顶+时间排序"""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM clipboard_items ORDER BY is_pinned DESC, created_at DESC"
            ).fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise RuntimeError(f"查询记录失败: {e}") from e
        finally:
            conn.close()

    def search_items(self, keyword):
        """搜索文字记录"""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM clipboard_items WHERE content_type = 'text' AND text_content LIKE ? ORDER BY is_pinned DESC, created_at DESC",
                ('%' + keyword + '%',)
            ).fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise RuntimeError(f"搜索记录失败: {e}") from e
        finally:
            conn.close()

    def get_item_by_id(self, item_id):
        """根据 ID 获取单条记录"""
        conn = self._get_conn()
        try:
            row = conn.execute("SELECT * FROM clipboard_items WHERE id = ?", (item_id,)).fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            raise RuntimeError(f"查询记录失败: {e}") from e
        finally:
            conn.close()
