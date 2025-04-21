from card.dao import CardDAO
from decimal import Decimal, getcontext

getcontext().prec = 10

def transfer_money(user, data):
    answer = CardDAO.transaction(user, data)
    return answer

def delete_card(user, data):
    card_number = data['card_number']
    return CardDAO.delete_card(user, card_number)

def add_product(user, data):
    card = CardDAO.add_card(user, data['product_type'], data["is_named_product"], data['currency'])
    return card