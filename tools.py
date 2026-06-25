from sqlalchemy.orm import Session
from fastapi import Query

def get_page_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    offset = (page - 1) * page_size
    return page, page_size, offset

def paginate_query(db: Session, query, offset, page_size):
    total = query.count()
    data = query.limit(page_size).offset(offset).all()
    total_page = (total + page_size - 1) // page_size
    return {
        "list": data,
        "page": offset // page_size + 1,
        "page_size": page_size,
        "total": total,
        "total_page": total_page
    }