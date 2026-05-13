"""
图片工具模块 - 图片保存与缩略图生成
"""

import os
from io import BytesIO
from PIL import Image
from PyQt5.QtCore import QBuffer, QIODevice


def _qimage_to_pil(qimage):
    """QImage → PIL Image（通过 QBuffer 中转，不依赖 ImageQt）"""
    if qimage.isNull():
        raise ValueError("QImage 为空，无法转换")
    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)
    if not qimage.save(buffer, 'PNG'):
        raise RuntimeError("QImage 保存到缓冲区失败，图片可能已损坏")
    try:
        return Image.open(BytesIO(buffer.data()))
    except Exception as e:
        raise RuntimeError(f"PIL 无法解析图片数据: {e}") from e


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
    try:
        pil_image.save(image_path, 'PNG')
    except OSError as e:
        raise RuntimeError(f"图片写入磁盘失败 (路径: {image_path}): {e}") from e

    # 生成缩略图
    try:
        thumb = pil_image.copy()
        thumb.thumbnail((200, 200), Image.LANCZOS)
        thumb.save(thumb_path, 'PNG')
    except Exception as e:
        # 缩略图生成失败属于非致命错误，删除可能产生的残缺文件，抛出异常
        if os.path.exists(thumb_path):
            try:
                os.remove(thumb_path)
            except OSError:
                pass
        try:
            os.remove(image_path)
        except OSError:
            pass
        raise RuntimeError(f"缩略图生成失败: {e}") from e

    return image_path, thumb_path


def load_thumbnail(thumb_path, max_size=(200, 200)):
    """加载缩略图，失败时返回 None"""
    try:
        if os.path.exists(thumb_path):
            return Image.open(thumb_path)
    except Exception:
        pass
    return None
