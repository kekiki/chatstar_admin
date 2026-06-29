from io import BytesIO
from PIL import Image
import os

def compress_image(image_bytes: bytes, max_size: int = 300, quality: int = 85) -> bytes:
    """
    压缩图片
    :param image_bytes: 图片二进制数据
    :param max_size: 最大尺寸（宽或高），默认300px
    :param quality: JPEG质量，默认85
    :return: 压缩后的图片二进制数据
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        
        # 转换为RGB模式（如果是RGBA）
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # 计算缩放比例
        width, height = img.size
        if width > height:
            if width > max_size:
                new_width = max_size
                new_height = int(height * (max_size / width))
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            if height > max_size:
                new_height = max_size
                new_width = int(width * (max_size / height))
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 压缩并保存到BytesIO
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        compressed_bytes = output.getvalue()
        
        return compressed_bytes
    except Exception as e:
        raise Exception(f"图片压缩失败: {str(e)}")
