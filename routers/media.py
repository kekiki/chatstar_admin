from fastapi import APIRouter, Request, Depends, Query, Body, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_, cast, String
from database import get_db
from tools import get_page_params, paginate_query
import models
import os
import tempfile
from aws_s3_client import AWSS3Client
from image_utils import compress_image

# Optional import for video thumbnail generation
try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def generate_video_thumbnail(video_bytes, filename):
    """Generate thumbnail from video bytes."""
    if not MOVIEPY_AVAILABLE:
        print("moviepy not installed, skipping thumbnail generation")
        return None
    
    try:
        # Create temporary file for video
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
            temp_video.write(video_bytes)
            temp_video_path = temp_video.name
        
        # Generate thumbnail using moviepy
        clip = VideoFileClip(temp_video_path)
        # Get frame at 1 second (or middle if video is shorter)
        thumbnail_time = min(1.0, clip.duration / 2) if clip.duration > 0 else 0
        frame = clip.get_frame(thumbnail_time)
        
        # Save thumbnail to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_thumb:
            from PIL import Image
            img = Image.fromarray(frame)
            img.save(temp_thumb.name, 'JPEG')
            temp_thumb_path = temp_thumb.name
        
        # Read thumbnail bytes
        with open(temp_thumb_path, 'rb') as f:
            thumbnail_bytes = f.read()
        
        # Clean up temporary files
        os.unlink(temp_video_path)
        os.unlink(temp_thumb_path)
        
        return thumbnail_bytes
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return None

@router.get("/admin/media", response_class=HTMLResponse)
async def media_list(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1),
    page_size: int = Query(10),
    keyword: str = Query("", description="全字段模糊搜索"),
    is_video: str = Query(None, description="是否视频筛选, true/false"),
    is_vip: str = Query(None, description="是否VIP筛选, true/false"),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    page, page_size, offset = get_page_params(page, page_size)
    q = db.query(models.Media).order_by(models.Media.created_time.desc())

    if keyword:
        q = q.filter(
            or_(
                cast(models.Media.user_id, String).like(f"%{keyword}%"),
            )
        )

    # 处理 is_video 筛选
    if is_video is not None and is_video != "":
        if str(is_video).lower() in ("1", "true", "yes"):
            q = q.filter(models.Media.is_video == True)
        elif str(is_video).lower() in ("0", "false", "no"):
            q = q.filter(models.Media.is_video == False)

    # 处理 is_vip 筛选
    if is_vip is not None and is_vip != "":
        if str(is_vip).lower() in ("1", "true", "yes"):
            q = q.filter(models.Media.is_vip == True)
        elif str(is_vip).lower() in ("0", "false", "no"):
            q = q.filter(models.Media.is_vip == False)

    page_data = paginate_query(db, q, offset, page_size)
    return templates.TemplateResponse(request, "media_list.html", {
        "request": request,
        "active_menu": "media",
        "page_data": page_data,
        "keyword": keyword,
        "is_video": is_video,
        "is_vip": is_vip
    })

@router.post("/admin/api/upload_media")
async def upload_media(
    request: Request,
    file: UploadFile = File(...),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    from database import get_db
    db = next(get_db())
    _user = require_login(request, db)
    
    # 检查文件类型
    if not file.content_type or (not file.content_type.startswith('image/') and not file.content_type.startswith('video/')):
        return {"code": 400, "msg": "只支持图片或视频文件"}
    
    try:
        # 读取文件内容
        file_bytes = await file.read()
        file_content_type = file.content_type

        # 如果是图片，先进行缩放/压缩/转码，尽量减小体积并保持清晰度
        upload_bytes = file_bytes
        upload_content_type = file_content_type
        upload_filename = file.filename
        if file_content_type and file_content_type.startswith('image/'):
            try:
                comp = compress_image(file_bytes, max_width=1080, quality=85)
                upload_bytes = comp.get("bytes", file_bytes)
                upload_content_type = comp.get("content_type", file_content_type)
                base = file.filename.rsplit('.', 1)[0] if '.' in file.filename else file.filename
                ext = comp.get("ext") or (file.filename.rsplit('.', 1)[-1] if '.' in file.filename else '')
                upload_filename = f"{base}.{ext}" if ext else upload_filename
            except Exception as e:
                print(f"Image compress failed, will upload original: {e}")

        aws_s3_client = AWSS3Client()
        link_info = aws_s3_client.upload_and_get_link(upload_bytes, upload_filename, upload_content_type)
        
        cover_url = None
        # 如果是视频，自动生成封面
        if file_content_type.startswith('video/'):
            print(f"Video detected, generating thumbnail...")
            thumbnail_bytes = generate_video_thumbnail(file_bytes, file.filename)
            if thumbnail_bytes:
                print(f"Thumbnail generated successfully, uploading...")
                thumbnail_filename = f"thumb_{file.filename.rsplit('.', 1)[0]}.jpg"
                cover_info = aws_s3_client.upload_and_get_link(thumbnail_bytes, thumbnail_filename, 'image/jpeg')
                cover_url = cover_info["url"]
                print(f"Thumbnail uploaded: {cover_url}")
            else:
                print(f"Thumbnail generation failed or moviepy not available")
        
        return {
            "code": 200,
            "msg": "上传成功",
            "url": link_info["url"],
            "cover": cover_url
        }
    except Exception as e:
        return {"code": 500, "msg": f"上传失败: {str(e)}"}

@router.post("/admin/api/add_media")
async def add_media(
    request: Request,
    url: str = Body(""),
    cover: str = Body(""),
    user_id: int = Body(0),
    is_vip: bool = Body(False),
    is_video: bool = Body(False),
    db: Session = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    new_media = models.Media(
        user_id=user_id,
        url=url,
        cover=cover,
        is_vip=is_vip,
        is_video=is_video
    )
    db.add(new_media)
    db.commit()
    db.refresh(new_media)
    return {
        "code": 200,
        "msg": "新增成功",
        "media": {
            "id": new_media.id,
            "user_id": new_media.user_id,
            "url": new_media.url,
            "cover": new_media.cover,
            "is_vip": new_media.is_vip,
            "is_video": new_media.is_video
        }
    }

@router.put("/admin/api/update_media")
async def update_media(
    request: Request,
    id: int = Body(...),
    user_id: int = Body(None),
    url: str = Body(None),
    cover: str = Body(None),
    is_vip: bool = Body(False),
    is_video: bool = Body(None),
    db: Session = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    media = db.query(models.Media).filter(models.Media.id == id).first()
    if not media:
        return {"code": 404, "msg": "媒体不存在"}

    if url is not None and url != "":
        media.url = url
    if cover is not None and cover != "":
        media.cover = cover
    if user_id is not None:
        media.user_id = user_id
    if is_vip is not None:
        media.is_vip = is_vip
    if is_video is not None:
        media.is_video = is_video

    db.commit()
    db.refresh(media)
    return {
        "code": 200,
        "msg": "更新成功",
        "media": {
            "id": media.id,
            "user_id": media.user_id,
            "url": media.url,
            "cover": media.cover,
            "is_vip": media.is_vip,
            "is_video": media.is_video
        }
    }

@router.delete("/admin/api/delete_media")
async def delete_media(
    request: Request,
    id: int = Query(...),
    db: Session = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    media = db.query(models.Media).filter(models.Media.id == id).first()
    if not media:
        return {"code": 404, "msg": "媒体不存在"}
    db.delete(media)
    db.commit()
    return {"code": 200, "msg": "删除成功"}
