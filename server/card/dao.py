from sqlalchemy import select, insert, update, inspect
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import flag_modified
from decimal import Decimal, getcontext
from datetime import datetime

from dao.base import BaseDAO
from user.dao import UsersDAO
from modules.database import Session

from data.service import credit_info, entity_data
from card.models import Card
from user.models import User
from background_process.currency import currency



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
    def delete_card(cls, user, card_number):
        with Session() as session:
            # Проверяем, привязан ли объект user к текущей сессии
            if user not in session:
                # Если объект не привязан к сессии, загружаем его заново
                user_id = user.id
                user = session.get(User, user_id)
                if not user:
                    raise ValueError("Пользователь не найден")

            card = session.query(Card).filter_by(card_number=card_number).first()
            if not card:
                return {"status": 404, "details": "Карта не найдена"}

            if card.owner != user:
                return {"status": 403, "details": "Это не ваша карта)"}

            if card.balance >= 0.01:
                return {"status": 400, "details": "Перед удалением надо вывести деньги"}

            session.delete(card)
            session.commit()
            return {"status": 200, "details": "Карта удалена"}

    @classmethod
    def transaction(cls, user, data):
        with (Session() as session):
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

                if transfer_type == 'Телефону':
                    user_output = UsersDAO.find_one_or_none(telephone=adr)
                    if not user_output:
                        return {"status": 404, "details": "Пользователь не найден"}
                    if user_output.id == user.id:
                        return {"status": 400, "details": "Вы не можете перевести деньги себе"}
                    for card in user_output.cards:
                        if card.currency == card_inp.currency and card.type == "Дебетовая карта":
                            card_out = (session.query(Card).filter_by(card_number=card.card_number).first())#СУПЕР ПРИКОЛ ДЛЯ ТОГО ЧТОБ КАРТА БЫЛА В СЕССИИИ
                            break
                    else:
                        return {"status": 400, "details": "У юзера\nНет дебетовой карты для перевода\nВ этой валюте"}
                else:
                    card_out = (session.query(Card).filter_by(card_number=adr).first())

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

                if card_out.type in ["Кредитная карта", "Кредит"] and card_out.balance + amount > 0:
                    return {"status": 400, "details": "на кредитной карте не может быть больше 0"}

                # Перевод
                if card_inp.currency != card_out.currency and card_inp.owner == card_out.owner:
                    loc_curency = currency.to_dict()
                    if card_inp.currency == "BYN":
                        inp_amount_byn = amount
                    else:
                        inp_amount_byn = amount * (Decimal("1") / Decimal(str(loc_curency[card_inp.currency]['buy'])))

                    if card_out.currency == "BYN":
                        out_amount = inp_amount_byn
                    else:
                        out_amount = inp_amount_byn * Decimal(str(loc_curency[card_out.currency]['sell']))

                    card_inp.balance -= amount
                    card_out.balance += out_amount

                else:
                    card_inp.balance -= amount
                    card_out.balance += amount

                card_inp.transactions.append(f"Отправлено: {amount} на {card_out.card_number}    -   {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}")
                card_out.transactions.append(f"Получено:  {amount} от {card_inp.card_number}   -   {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}")
                flag_modified(card_inp, "transactions")
                flag_modified(card_out, "transactions")
                card_inp.last_transaction = datetime.now()
                card_out.last_transaction = datetime.now()
                session.commit()
                print(f"!!!!!!!!!!!!!!!log {datetime.now()}: перевод {amount} с карты {card_inp.card_number} на карту {card_out.card_number}")
                return {"status": 200, "details": "Успешно переведено"}

            except Exception as e:
                session.rollback()
                raise e
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

            if len(owner.cards) >= 8:
                raise ValueError({"status": 400, "details": "Превышен лимит карт"})

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
