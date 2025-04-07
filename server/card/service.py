from card.dao import CardDAO
from decimal import Decimal, getcontext

getcontext().prec = 10

def add_product(user, data):
    card = CardDAO.add_card(user, data['product_type'], data["is_named_product"], data['currency'])
    return card