
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

conn_string = "postgresql+asyncpg://postgres:vWuC7Zwsx%40BxZC%24Xp%25%245@db.pwuczqnnxstvxbfnwkls.supabase.co:5432/postgres"


engine = create_async_engine(conn_string, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
