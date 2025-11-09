import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

db_url = os.getenv("DATABASE_URL", "
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(db_url, echo=False, future=True)
Session = async_sessionmaker(engine, expire_on_commit=False)
