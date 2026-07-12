from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Query

def get_page_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    offset = (page - 1) * page_size
    return page, page_size, offset

async def paginate_query(db: AsyncSession, query, offset, page_size):
    count_stmt = select(func.count()).select_from(query.order_by(None).subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    page_stmt = query.limit(page_size).offset(offset)
    result = await db.execute(page_stmt)
    data = result.scalars().all()

    total_page = (total + page_size - 1) // page_size
    return {
        "list": data,
        "page": offset // page_size + 1,
        "page_size": page_size,
        "total": total,
        "total_pages": total_page
    }
