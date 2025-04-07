from dao.base import BaseDAO
from modules.database import Session
from card.models import Card
from user.models import User
from sqlalchemy import select, insert, update
from sqlalchemy.orm import joinedload

from data.service import credit_info, entity_data



class CardDAO(BaseDAO):
    model = Card

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
    def add_card(cls,
            owner, type, is_named, currency):
        with Session() as session:
            # Проверяем, привязан ли объект owner к текущей сессии
            if owner not in session:
                # Если объект не привязан к сессии, загружаем его заново
                owner_id = owner.id
                owner = session.get(User, owner_id)
                if not owner:
                    raise ValueError("Пользователь не найден")

            if is_named:
                card_name = f"{owner.name} {owner.surname}"
            else:
                card_name = "Incognit"

            if not (
                    (type in ["Дебетовая карта", "Кредитная карта",
                     "Овердрафтная карта", "Кредит", "Копилка", "Криптокарта"]
                    and currency in ["BYN", "USD", "EUR", "RUB"] )
                    or (type == "Криптокарта" and currency == "SHD")) :
                raise ValueError("НЕВЕРНЫЙ ТИП КАРТЫ ИЛИ ВАЛЮТА")


            if type in ["Кредитная карта", "Овердрафтная карта", "Кредит", "Копилка"]:
                procent = credit_info.data[type][currency]["procent"]
                limit = credit_info.data[type][currency]["limit"]
            else:
                procent = 0
                limit = 1000000

            last_card = session.query(Card).order_by(Card.id.desc()).first()
            if last_card:
                last_id = last_card.id
            else:
                last_id = 0
            last_id += 1
            card_number = f"{entity_data.data['card_start']}{last_id:08d}"


            new_card = Card(
                owner=owner,
                type=type,
                owner_card= card_name,
                currency=currency,
                procent=procent,
                limit=limit,
                card_number=card_number
            )
            session.add(new_card)
            session.commit()
            return new_card
