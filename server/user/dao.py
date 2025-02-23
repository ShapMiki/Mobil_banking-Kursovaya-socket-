from dao.base import BaseDAO
from modules.database import async_session_maker
from users.models import Users
from sqlalchemy import select, insert, update


class UsersDAO(BaseDAO):
    model = Users

    @classmethod
    async def update_balance(cls, id, ballance):
        async with async_session_maker() as session:
            query = update(cls.model).values(ballance=ballance).where(cls.model.id == id)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def update_one(cls, id, **kwargs):
        async with async_session_maker() as session:
            query = cls.model.__table__.update().values(**kwargs).where(cls.model.id == id)
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def add_one(email: str, name: str, password: str, surname: str = None):
        async with async_session_maker() as session:
            new_user = Users(email=email, name=name, password=password, surname=surname)
            session.add(new_user)
            await session.commit()
            return new_user