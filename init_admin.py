import asyncio

from database import AsyncSessionLocal, engine, Base
import models
import auth


async def init_db_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_admin_user():
    async with AsyncSessionLocal() as session:
        hash_pwd = auth.get_password_hash("123456")
        admin = models.AdminUser(username="admin", password=hash_pwd)
        session.add(admin)
        await session.commit()
    print("管理员创建成功，账号admin，密码123456")


async def main():
    await init_db_tables()
    await create_admin_user()


if __name__ == "__main__":
    asyncio.run(main())
