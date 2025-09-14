import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
engine = create_async_engine(os.getenv("DATABASE_URL"), echo=False, future=True)
Session = async_sessionmaker(engine, expire_on_commit=False)
