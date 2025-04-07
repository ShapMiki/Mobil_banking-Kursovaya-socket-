from decimal import Decimal, ROUND_DOWN
from datetime import datetime


def get_user_data(user):
    try:
        cards = []
        for card in user.cards:
            card_data = {
                'card_number': card.card_number,
                "owner_card": card.owner_card,
                'valid_to': card.valid_to.strftime("%m/%Y"),
                'cvv': card.cvv,
                'pin': card.pin,
                'type': card.type,
                'currency': card.currency,
                'balance': str(Decimal(str(card.balance)).quantize(Decimal('0.01'), rounding=ROUND_DOWN))
            }
            cards.append(card_data)


        user_data = {
            'name': user.name,
            'surname': user.surname,
            'passport_number': user.passport_number,
            'passport_id': user.passport_id,
            'telephone': user.telephone,
            'cards': cards
        }
        return user_data


    except Exception as e:
        return {"status": 500, "details": str(e)}