"""
性能验证 — 大数据量下的加载和搜索速度
"""

import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import Database


def benchmark(record_count):
    """用临时数据库测试性能，返回各项耗时（秒）"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    db = Database(db_path=path)

    # 批量插入
    start = time.time()
    for i in range(record_count):
        db.add_item('text', text_content=f'这是第 {i} 条测试记录，包含一些中文和数字 {i * 7}')
    insert_elapsed = time.time() - start

    # 查询全部
    start = time.time()
    items = db.get_all_items()
    query_elapsed = time.time() - start
    assert len(items) == record_count

    # 搜索
    start = time.time()
    results = db.search_items('测试')
    search_elapsed = time.time() - start
    assert len(results) == record_count

    # 标记过期
    start = time.time()
    db.mark_expired(retention_days=3)
    mark_elapsed = time.time() - start

    os.remove(path)

    return insert_elapsed, query_elapsed, search_elapsed, mark_elapsed


if __name__ == '__main__':
    print(f'{"记录数":>8}  {"插入(s)":>10}  {"查询(s)":>10}  {"搜索(s)":>10}  {"标记(s)":>10}')
    print('-' * 60)

    for count in [1000, 5000, 10000]:
        insert_t, query_t, search_t, mark_t = benchmark(count)
        print(f'{count:>8}  {insert_t:>10.3f}  {query_t:>10.3f}  {search_t:>10.3f}  {mark_t:>10.3f}')

    print()
    print('验收标准: 查询、搜索 < 0.5s，插入 10000 条 < 10s')
