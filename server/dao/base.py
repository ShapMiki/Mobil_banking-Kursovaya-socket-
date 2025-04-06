from modules.database import Session
from sqlalchemy import select, insert
from sqlalchemy.orm import joinedload

class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none(cls, **kwargs):
        async with Session() as session:
            query = select(cls.model).filter_by(**kwargs)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    def add_one(cls, model):
        with Session() as session:
            session.add(model)
            session.commit()

    @classmethod
    def find_all(cls):
        with Session() as session:
            query = select(cls.model)
            # Загружаем все связанные отношения
            for relationship in cls.model.__mapper__.relationships:
                query = query.options(joinedload(relationship))
            result = session.execute(query)
            # Используем unique() для результатов с коллекциями
            return result.unique().scalars().all()

    @classmethod
    def find_by_id(cls, user_id: int):
        with Session() as session:
            query = select(cls.model).filter_by(id=user_id)
            # Загружаем все связанные отношения
            for relationship in cls.model.__mapper__.relationships:
                query = query.options(joinedload(relationship))
            result = session.execute(query)
            # Используем unique() для результатов с коллекциями
            return result.unique().scalar_one_or_none()

    @classmethod
    def create(cls, obj):
        with Session() as session:
            with session.begin():
                session.add(obj)
                session.commit()
                return obj

    @classmethod
    def update(cls, obj):
        with Session() as session:
             with session.begin():
                session.merge(obj)
                session.commit()
                return obj

    @classmethod
    def delete(cls, obj):
        with Session() as session:
             with session.begin():
                session.delete(obj)
                session.commit()
                return obj

    @classmethod
    def delete_by_id(cls, id):
        with Session() as session:
            with session.begin():
                query = select(cls.model).filter_by(id=id)
                result = session.execute(query)
                obj = result.scalar_one_or_none()
                if obj:
                    session.delete(obj)
                    session.commit()
                return obj