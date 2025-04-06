


def get_user_data(user):
    try:
        user_data = {
            'name': user.name,
            'surname': user.surname,
            'passport_number': user.passport_number,
            'passport_id': user.passport_id,
            'telephone': user.telephone,
            'cards': user.cards
        }
        return user_data

    except Exception as e:
        return {"status": 500, "details": str(e)}