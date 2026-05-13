"""
image_utils.py 单元测试
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.image_utils import save_image_from_qimage, _qimage_to_pil, load_thumbnail
from PyQt5.QtGui import QImage


class TestQimageToPil:
    def test_valid_image(self):
        """正常 QImage 转换"""
        img = QImage(100, 100, QImage.Format_ARGB32)
        img.fill(0xFF336699)
        pil_img = _qimage_to_pil(img)
        assert pil_img is not None
        assert pil_img.size == (100, 100)

    def test_null_image_raises(self):
        """空 QImage 抛出异常"""
        with pytest.raises(ValueError, match='QImage 为空'):
            _qimage_to_pil(QImage())


class TestSaveImageFromQimage:
    def test_save_valid_image(self):
        """正常保存图片，验证文件生成"""
        img = QImage(400, 400, QImage.Format_ARGB32)
        img.fill(0xFFFF0000)

        with tempfile.TemporaryDirectory() as tmpdir:
            images_dir = os.path.join(tmpdir, 'images')
            thumbs_dir = os.path.join(tmpdir, 'thumbnails')
            os.makedirs(images_dir)
            os.makedirs(thumbs_dir)

            import src.paths as paths
            original_get_images_dir = paths.get_images_dir
            original_get_thumbnails_dir = paths.get_thumbnails_dir
            paths.get_images_dir = lambda: images_dir
            paths.get_thumbnails_dir = lambda: thumbs_dir

            try:
                image_path, thumb_path = save_image_from_qimage(img, 'test123')
                assert os.path.exists(image_path)
                assert os.path.exists(thumb_path)
                # 验证缩略图比原图小
                img_size = os.path.getsize(image_path)
                thumb_size = os.path.getsize(thumb_path)
                assert thumb_size < img_size
            finally:
                paths.get_images_dir = original_get_images_dir
                paths.get_thumbnails_dir = original_get_thumbnails_dir


class TestLoadThumbnail:
    def test_load_existing_thumbnail(self):
        """加载存在的缩略图"""
        img = QImage(30, 30, QImage.Format_ARGB32)
        img.fill(0xFF00FF00)

        with tempfile.TemporaryDirectory() as tmpdir:
            thumb_path = os.path.join(tmpdir, 'thumb.png')
            # 先生成缩略图
            pil_img = _qimage_to_pil(img)
            thumb = pil_img.copy()
            thumb.thumbnail((30, 30))
            thumb.save(thumb_path, 'PNG')

            loaded = load_thumbnail(thumb_path)
            assert loaded is not None
            assert loaded.size[0] <= 30
            # 关闭 PIL 图片，避免 Windows 下文件句柄冲突
            loaded.close()

    def test_load_nonexistent_thumbnail(self):
        """加载不存在的文件返回 None"""
        result = load_thumbnail('/nonexistent/path/thumb.png')
        assert result is None
