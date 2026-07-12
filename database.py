from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from urllib.parse import urlencode, parse_qsl, urlparse, urlunparse
from config import DATABASE_URL


def build_async_engine_url(database_url: str):
    """Convert a sync PostgreSQL URL to asyncpg format and normalize SSL args."""
    async_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    parsed = urlparse(async_url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    connect_args = {}

    # asyncpg connect() does not accept sslmode/channel_binding directly.
    # Convert common Neon SSL parameters into supported connect args.
    sslmode = query.pop("sslmode", None)
    query.pop("channel_binding", None)
    if sslmode in ("require", "verify-ca", "verify-full"):
        connect_args["ssl"] = True
    elif sslmode == "disable":
        connect_args["ssl"] = False

    cleaned_url = urlunparse(parsed._replace(query=urlencode(query)))
    return cleaned_url, connect_args


ASYNC_DATABASE_URL, ASYNC_CONNECT_ARGS = build_async_engine_url(DATABASE_URL)

# 内置连接池配置（适配Neon休眠，控制连接数省CU）
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    connect_args=ASYNC_CONNECT_ARGS,
    pool_size=3,        # 常驻连接
    max_overflow=8,     # 峰值额外连接
    pool_recycle=300,   # 5分钟回收闲置连接，解决Neon断开
    echo=False
)

# 会话工厂，自动从池拿连接、用完归还
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

# 所有表的父类
Base = declarative_base()

# 启动时自动创建所有不存在的表
async def init_db_tables():
    # 关键：导入models包，加载所有模型到Base.metadata
    import models
    async with engine.begin() as conn:
        # 扫描所有继承Base的模型，不存在则新建表
        await conn.run_sync(Base.metadata.create_all)

# FastAPI全局依赖，每个请求自动分配会话
async def get_db():
    # 首次请求执行一次建表，重复调用无害
    await init_db_tables()
    async with AsyncSessionLocal() as session:
        yield session
        # 离开作用域自动归还连接到池
