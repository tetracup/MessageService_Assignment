
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
#conn_string = "postgresql+asyncpg://postgres.pwuczqnnxstvxbfnwkls:vWuC7Zwsx%40BxZC%24Xp%25%245@aws-0-eu-north-1.pooler.supabase.com:5432/postgres"
conn_string = os.getenv("DATABASE_URL")

engine = create_async_engine(conn_string, echo=True, connect_args={"statement_cache_size": 0})

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

