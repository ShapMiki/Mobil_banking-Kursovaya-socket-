from dao.base import BaseDAO
from modules.database import Session
from card.models import Card
from user.models import User
from sqlalchemy import select, insert, update, inspect
from sqlalchemy.orm import joinedload

from data.service import credit_info, entity_data

from decimal import Decimal, getcontext


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
    def transaction(cls, user, data):
        with Session() as session:
            try:
                adr = data['adr']
                card_number = data['card_number']
                transfer_type = data['transfer_type']
                try:
                    amount = Decimal(data['sum'])
                except:
                    return {"status": 400, "details": "Неверная сумма"}

                if amount < 0.1:
                    return {"status": 400, "details": "Слишком маленький перевод"}

                # Проверка, привязан ли пользователь к сессии
                if not inspect(user).persistent:
                    user = session.get(User, user.id)
                    if not user:
                        return {"status": 404, "details": "Пользователь не найден"}

                card_inp = session.query(Card).filter_by(card_number=card_number).first()

                card_out = (
                    session.query(Card).filter_by(telephone=adr).first()
                    if transfer_type == 'Телефону'
                    else session.query(Card).filter_by(card_number=adr).first()
                )

                if not card_inp or not card_out:
                    return {"status": 400, "details": "Карта не найдена"}

                if card_inp.currency != card_out.currency and card_inp.owner != card_out.owner:
                    return {"status": 400, "details": "Разные валюты"}

                if card_inp.owner != user:
                    return {"status": 403, "details": "Это не ваша карта)"}

                # Проверка лимита
                if card_inp.type in ["Кредитная карта", "Овердрафтная карта", "Кредит"]:
                    if card_inp.balance - amount < card_inp.limit:
                        return {"status": 400, "details": "Превышен лимит"}
                else:
                    if card_inp.balance - amount < 0:
                        return {"status": 400, "details": "Недостаточно средств на карте"}

                # Перевод
                if card_inp.currency != card_out.currency and card_inp.owner == card_out.owner:
                    pass  # TODO: сделать конвертацию
                else:
                    card_inp.balance -= amount
                    card_out.balance += amount

                session.commit()
                return {"status": 200, "details": "Успешно переведено"}

            except Exception as e:
                session.rollback()
                return {"status": 500, "details": f"Ошибка: {str(e)}"}


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
