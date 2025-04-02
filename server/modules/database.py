from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import settings

DATABASE_URL = settings.DATABASE_URL

# Создаём синхронный engine для работы в многопоточном режиме
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=1800)

# sessionmaker для синхронных сессий
Session = sessionmaker(bind=engine)

# Базовый класс для всех моделей
class Base(DeclarativeBase):
    pass
