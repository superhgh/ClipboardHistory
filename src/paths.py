"""
路径工具 - 统一处理开发环境和 PyInstaller 打包后的路径
"""

import sys
import os


def get_app_dir():
    """获取应用根目录（开发时=项目根，打包后=exe所在目录）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后
        return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_data_dir():
    """获取用户数据目录"""
    d = os.path.join(get_app_dir(), 'data')
    os.makedirs(d, exist_ok=True)
    return d


def get_db_path():
    """获取数据库文件路径"""
    return os.path.join(get_data_dir(), 'clipboard.db')


def get_images_dir():
    """获取图片存储目录"""
    d = os.path.join(get_data_dir(), 'images')
    os.makedirs(d, exist_ok=True)
    return d


def get_thumbnails_dir():
    """获取缩略图存储目录"""
    d = os.path.join(get_data_dir(), 'thumbnails')
    os.makedirs(d, exist_ok=True)
    return d
