from typing import Generator, AsyncGenerator
from contextlib import contextmanager, asynccontextmanager
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession

@asynccontextmanager
async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@contextmanager
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

