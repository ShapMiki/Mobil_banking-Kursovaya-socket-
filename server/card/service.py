from card.dao import CardDAO
from decimal import Decimal, getcontext

getcontext().prec = 10

def transfer_money(user, data):
    answer = CardDAO.transaction(user, data)
    return answer


def add_product(user, data):
    #TODO: Сделать проверку на количество карт
    card = CardDAO.add_card(user, data['product_type'], data["is_named_product"], data['currency'])
    return card