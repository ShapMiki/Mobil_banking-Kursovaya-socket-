from dao.base import BaseDAO
from modules.database import Session
from user.models import User
from sqlalchemy import select, insert, update
from sqlalchemy.orm import joinedload

class UsersDAO(BaseDAO):
    model = User

    @classmethod
    def find_one_or_none(cls, **kwargs):
        with Session() as session:
            query = select(cls.model).filter_by(**kwargs)

            for relationship in cls.model.__mapper__.relationships:
                query = query.options(joinedload(relationship))
            result = session.execute(query)
            return result.unique().scalar_one_or_none()

    @classmethod
    def update_balance(cls, id, ballance):
        with Session() as session:
            query = update(cls.model).values(ballance=ballance).where(cls.model.id == id)
            session.execute(query)
            session.commit()

    @classmethod
    def update_one(cls, id, **kwargs):
        with Session() as session:
            query = cls.model.__table__.update().values(**kwargs).where(cls.model.id == id)
            session.execute(query)
            session.commit()

    @classmethod
    def add_user(cls,
            name: str,  surname: str, passport_number:str,
            passport_id, telephone:str, password: str
                      ):
        with Session() as session:
            new_user = User(
                name=name, surname=surname, passport_number=passport_number,
                passport_id=passport_id, telephone=telephone, password=password
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return new_user