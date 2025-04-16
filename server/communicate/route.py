from datetime import datetime

from user.dao import UsersDAO
from user.auth import get_password_hash, authenticate_user, create_access_token, get_current_user
from user.service import get_user_data
from card.service import *
from background_process.currency import currency



router_dir = {
    'get': {},
    'post': {},
    'SECURITY_POST': {}
}

def router(method, route):
    def decorator(func):
        router_dir[method][route] = func
        return func
    return decorator


@router('get', 'check_start')
def check_start(data = None):
    return {"status": 200, "details": "Сервер запущен, get: get_congif для подробной информации"}

@router('get', 'get_config')
def get_name(data = None):
    return {}

@router('get', 'currency_api')
def get_currency(data = None):
    return currency.to_dict()

@router('post', 'transfer_money_api')
def transfer_money_api(data):
    user = get_current_user(data)
    if not user:
        return {"status": 401, "details": "Unauthorized"}
    answer =transfer_money(user, data['data'])
    return answer

@router('post', 'get_balance')
def get_balance(data):
    print(data)

@router('post', 'create_product_api')
def create_product_api(data):
    user = get_current_user(data)
    if not user:
        return {"status": 401, "details": "Unauthorized"}
    add_product(user, data['data'])


@router('post', 'delete_card_api')
def delete_card_api(data):
    user = get_current_user(data)
    if not user:
        return {"status": 401, "details": "Unauthorized"}

    return delete_card(user, data['data'])


@router('post', 'get_user_data_api')
def get_user_data_api(data):
    user = get_current_user(data)
    if not user:
        return {"status": 401, "details": "Unauthorized"}
    user_data = get_user_data(user)
    print(user_data)
    return user_data


@router('post', 'check_auth')
def check_auth(data):
    user = get_current_user(data)

    if not user:
        return {"status": 401, "details": "Unauthorized"}

    UsersDAO.update_one(user.id, last_seance=datetime.now())
    jwt = create_access_token(data={"sub": str(user.id)})
    return {"JWT": jwt, "Auth": True}

@router('post', 'registration')
def registrate(data):
    data = data['data']
    try:
        user = UsersDAO.add_user(
            name=data['name'],
            surname=data['surname'],
            passport_number=data['passport_number'],
            passport_id=data['passport_id'],
            telephone=data['telephone'],
            password=get_password_hash(data['password'])
        )
        
        # Получаем данные пользователя до закрытия сессии
        user_id = user.id
        user_key = user.key
        
        jwt = create_access_token(data={"sub": str(user_id)})
        return {'JWT': jwt, "key": user_key}
    except Exception as e:
        return {"status": 500, "details": f"Registration error: {str(e)}"}


@router('post', 'login')
def login(data):
    print(data)
    try:
        data = data['data']
        user = authenticate_user(data['telephone'], data['password'])
    except KeyError:
        return {"status": 401, "details": "Bad data"}
    except AttributeError:
        return {"status": 403, "details": "Неверный логин или пароль"}

    if not user:
        return {"status": 403, "details": "Неверный логин или пароль"}
    jwt = create_access_token(data={"sub": str(user.id)})
    key = user.key
    return {'JWT': jwt, "key":key}


@router('SECURITY_POST', 'set_balance')
def set_balance(data):
    print(data)


print(router_dir['get']['check_start'](None))