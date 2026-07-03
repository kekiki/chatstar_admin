from io import BytesIO
from PIL import Image
import os

def compress_image(image_bytes: bytes, max_width: int = 1080, quality: int = 85, prefer_webp: bool = True) -> dict:
    """
    在上传前压缩/转码图片：
    - 若宽度超过 `max_width`，按比例缩放到 `max_width`。
    - 尽量在保持清晰度的前提下减小体积，尝试生成 WebP（可带 alpha）和 JPEG（无 alpha），取体积更小者。

    返回字典: {"bytes": bytes, "content_type": str, "ext": str}
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        orig_format = img.format

        # 判断是否有 alpha 通道
        has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)

        # 统一转换模式以便后续保存（保留 alpha 则为 RGBA，否则用 RGB）
        if has_alpha:
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")

        width, height = img.size
        if width > max_width:
            new_width = max_width
            new_height = int(height * (max_width / width))
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 先尝试 WebP（支持有无 alpha）
        webp_buf = BytesIO()
        webp_kwargs = {"format": "WEBP", "quality": quality}
        try:
            img.save(webp_buf, **webp_kwargs)
            webp_bytes = webp_buf.getvalue()
        except Exception:
            webp_bytes = b""

        best_bytes = webp_bytes
        best_content_type = "image/webp" if webp_bytes else None
        best_ext = "webp" if webp_bytes else None

        # 如果没有 alpha，就尝试 JPEG（通常更广泛且仍然体积小）
        if not has_alpha:
            jpg_buf = BytesIO()
            img.save(jpg_buf, format="JPEG", quality=quality, optimize=True, progressive=True)
            jpg_bytes = jpg_buf.getvalue()
            if best_bytes:
                if len(jpg_bytes) < len(best_bytes):
                    best_bytes = jpg_bytes
                    best_content_type = "image/jpeg"
                    best_ext = "jpg"
            else:
                best_bytes = jpg_bytes
                best_content_type = "image/jpeg"
                best_ext = "jpg"

        # 如果生成的都比原图大，则直接返回原图（避免恶化）
        if best_bytes and len(image_bytes) <= len(best_bytes):
            # 使用原始格式的 content_type 和扩展名
            fmt = (orig_format or "").lower()
            if fmt == "png":
                return {"bytes": image_bytes, "content_type": "image/png", "ext": "png"}
            if fmt in ("jpeg", "jpg"):
                return {"bytes": image_bytes, "content_type": "image/jpeg", "ext": "jpg"}
            if fmt == "webp":
                return {"bytes": image_bytes, "content_type": "image/webp", "ext": "webp"}
            # fallback
            return {"bytes": image_bytes, "content_type": "application/octet-stream", "ext": fmt}

        # 若 best_bytes 为空（例如 PIL 不支持 WebP），则返回原图
        if not best_bytes:
            fmt = (orig_format or "").lower()
            if fmt == "png":
                return {"bytes": image_bytes, "content_type": "image/png", "ext": "png"}
            if fmt in ("jpeg", "jpg"):
                return {"bytes": image_bytes, "content_type": "image/jpeg", "ext": "jpg"}
            return {"bytes": image_bytes, "content_type": "application/octet-stream", "ext": fmt}

        return {"bytes": best_bytes, "content_type": best_content_type, "ext": best_ext}
    except Exception as e:
        raise Exception(f"图片压缩失败: {str(e)}")
