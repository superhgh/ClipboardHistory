"""
图片工具模块 - 图片保存与缩略图生成
"""

import os
from io import BytesIO
from PIL import Image
from PyQt5.QtCore import QBuffer, QIODevice


def _qimage_to_pil(qimage):
    """QImage → PIL Image（通过 QBuffer 中转，不依赖 ImageQt）"""
    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)
    qimage.save(buffer, 'PNG')
    return Image.open(BytesIO(buffer.data()))


def save_image_from_qimage(qimage, item_id, data_dir=None):
    """保存 QImage 到本地文件，返回 (原图路径, 缩略图路径)"""
    if data_dir is None:
        from src.paths import get_data_dir
        data_dir = get_data_dir()

    from src.paths import get_images_dir, get_thumbnails_dir
    images_dir = get_images_dir()
    thumbs_dir = get_thumbnails_dir()

    image_path = os.path.join(images_dir, f'{item_id}.png')
    thumb_path = os.path.join(thumbs_dir, f'{item_id}.png')

    # 保存原图
    pil_image = _qimage_to_pil(qimage)
    pil_image.save(image_path, 'PNG')

    # 生成缩略图
    thumb = pil_image.copy()
    thumb.thumbnail((200, 200), Image.LANCZOS)
    thumb.save(thumb_path, 'PNG')

    return image_path, thumb_path


def load_thumbnail(thumb_path, max_size=(200, 200)):
    """加载缩略图，失败时返回 None"""
    try:
        if os.path.exists(thumb_path):
            return Image.open(thumb_path)
    except Exception:
        pass
    return None
