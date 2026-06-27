from fastapi import APIRouter, Request, Depends, Query, Body
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from tools import get_page_params, paginate_query
import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/anchor", response_class=HTMLResponse)
async def anchor_list(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1),
    page_size: int = Query(10),
    keyword: str = Query("", description="全字段模糊搜索"),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    page, page_size, offset = get_page_params(page, page_size)
    q = db.query(models.Anchor)

    if keyword:
        q = q.filter(
            or_(
                models.Anchor.id.like(f"%{keyword}%"),
                models.Anchor.nickname.like(f"%{keyword}%"),
                models.Anchor.country.like(f"%{keyword}%"),
                models.Anchor.language_name.like(f"%{keyword}%"),
                models.Anchor.language_code.like(f"%{keyword}%")
            )
        )

    page_data = paginate_query(db, q, offset, page_size)
    return templates.TemplateResponse(request, "anchor_list.html", {
        "request": request,
        "active_menu": "anchor",
        "page_data": page_data,
        "keyword": keyword
    })

@router.post("/admin/api/add_anchor")
async def add_anchor(
    request: Request,
    nickname: str = Body(...),
    avatar: str = Body(""),
    country: str = Body("US"),
    language_name: str = Body("English"),
    language_code: str = Body("en"),
    follow_count: int = Body(0),
    fans_count: int = Body(0),
    like_count: int = Body(0),
    is_check: bool = Body(False),
    db: Session = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    new_anchor = models.Anchor(
        nickname=nickname,
        avatar=avatar,
        country=country,
        language_name=language_name,
        language_code=language_code,
        follow_count=follow_count,
        fans_count=fans_count,
        like_count=like_count,
        is_check=is_check
    )
    db.add(new_anchor)
    db.commit()
    db.refresh(new_anchor)
    return {
        "code": 200,
        "msg": "新增成功",
        "anchor": {
            "id": new_anchor.id,
            "nickname": new_anchor.nickname,
            "avatar": new_anchor.avatar,
            "country": new_anchor.country,
            "language_name": new_anchor.language_name,
            "language_code": new_anchor.language_code,
            "follow_count": new_anchor.follow_count,
            "fans_count": new_anchor.fans_count,
            "like_count": new_anchor.like_count,
            "is_check": new_anchor.is_check
        }
    }

@router.put("/admin/api/update_anchor")
async def update_anchor(
    request: Request,
    id: int = Body(...),
    nickname: str = Body(None),
    avatar: str = Body(None),
    country: str = Body(None),
    language_name: str = Body(None),
    language_code: str = Body(None),
    follow_count: int = Body(None),
    fans_count: int = Body(None),
    like_count: int = Body(None),
    is_check: bool = Body(None),
    db: Session = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    anchor = db.query(models.Anchor).filter(models.Anchor.id == id).first()
    if not anchor:
        return {"code": 404, "msg": "主播不存在"}

    if nickname is not None:
        anchor.nickname = nickname
    if avatar is not None:
        anchor.avatar = avatar
    if country is not None:
        anchor.country = country
    if language_name is not None:
        anchor.language_name = language_name
    if language_code is not None:
        anchor.language_code = language_code
    if follow_count is not None:
        anchor.follow_count = follow_count
    if fans_count is not None:
        anchor.fans_count = fans_count
    if like_count is not None:
        anchor.like_count = like_count
    if is_check is not None:
        anchor.is_check = is_check

    db.commit()
    db.refresh(anchor)
    return {
        "code": 200,
        "msg": "更新成功",
        "anchor": {
            "id": anchor.id,
            "nickname": anchor.nickname,
            "avatar": anchor.avatar,
            "country": anchor.country,
            "language_name": anchor.language_name,
            "language_code": anchor.language_code,
            "follow_count": anchor.follow_count,
            "fans_count": anchor.fans_count,
            "like_count": anchor.like_count,
            "is_check": anchor.is_check
        }
    }

@router.delete("/admin/api/delete_anchor")
async def delete_anchor(
    request: Request,
    id: int = Query(...),
    db: Session = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    anchor = db.query(models.Anchor).filter(models.Anchor.id == id).first()
    if not anchor:
        return {"code": 404, "msg": "主播不存在"}
    db.delete(anchor)
    db.commit()
    return {"code": 200, "msg": "删除成功"}
