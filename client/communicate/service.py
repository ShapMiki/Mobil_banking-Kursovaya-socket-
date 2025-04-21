from communicate.client import client
from json import load, dump
import asyncio



def delete_card_serv(card_number)-> dict:
    """Удаляет карту по номеру карты"""
    data = {
        'card_number': card_number
    }
    answer = client.post('delete_card_api', data)
    try:
        return answer['details']
    except KeyError:
        raise ConnectionError('Ошибка удаления карты')


def get_currency() -> dict:
    """Получает курс валют"""
    answer = client.get('currency_api')
    try:
        currency = answer["data"]

        currency["RUB"]['buy'] *= 0.01
        currency['RUB']['sell'] *= 0.01
        for i in currency:
            currency[i]['buy'] = round(1/currency[i]['buy'], 2)
            currency[i]['sell'] = round(1/currency[i]['sell'], 2)

        return currency

    except KeyError:
        return answer['details']


def transfer_service(card_number, adr, sum, transfer_type) -> dict:
    """
    Переводит деньги с карты на карту
    args: card_number - номер карты, adr - номер карты или телефон, sum - сумма перевода, transfer_type - тип перевода
    """
    data = {
        'card_number': card_number,
        "transfer_type": transfer_type,
        'adr': adr,
        'sum': sum
    }
    answer = client.post('transfer_money_api', data)
    return answer["data"]['details']


def create_product(product_type, is_named_product, currency)-> None:
    """ Создает карту/счет """
    data = {
        'product_type': product_type,
        'is_named_product': is_named_product,
        'currency': currency
    }
    try:
        client.post('create_product_api', data)
    except ConnectionError as e:
        raise e


def quit_account() -> None:
    """Выход из аккаунта"""
    with open("data/server_config.json", "r") as json_file:
        config = load(json_file)

    config['JWT'] = None
    config["key"] = None
    client.config['JWT'] = None
    client.config["key"] = None

    with open("data/server_config.json", "w") as json_file:
        dump(config, json_file)

    client.update_json()

def check_auth() -> bool:
    """Проверяет авторизацию"""
    try:
        answer = client.post('check_auth', {})
    except ConnectionRefusedError as e:
        raise e
    except ConnectionError:
        return False
    except Exception as e:
       raise ConnectionRefusedError

    try:
         client.update_jwt(answer['data']['JWT'])
    except KeyError:
        return False
    return True


def get_user_data()-> dict:
    """Получает данные пользователя"""
    answer = client.post("get_user_data_api", {})
    try:
        user_data = answer['data']
    except KeyError:
        return answer['details']
    return user_data

async def login(phone, password)->bool:
    """Авторизация"""
    if not phone or not password:
        raise ValueError('Все поля должны быть заполнены')

    answer = client.post('login', {
        'telephone': phone,
        'password': password
    })

    with open("data/server_config.json", "r") as json_file:
       config = load(json_file)

    try:
        jwt_token = answer['data']['JWT']
        config['JWT'] = jwt_token
        config["key"] = answer['data']["key"]
        # Обновляем JWT в клиенте
        client.update_jwt(jwt_token)
    except KeyError:
        raise ConnectionAbortedError('Неверный логин или пароль')
    
    with open("data/server_config.json", "w") as json_file:
        dump(config, json_file)

    client.update_json()

    return True


async def registration(name, surname, passport_number, passport, phone, password)-> bool:
    """Регистрация"""
    if not name or not surname or not passport_number or not passport or not phone or not password:
        raise ValueError('Все поля должны быть заполнены')

    if len(name) < 3 or len(surname) < 3:
        raise ValueError('Имя и фамилия должны быть длиннее 3 символов')

    if len(passport) != 14:
        raise ValueError('ID паспорта должен быть 14 символов')
    if len(passport_number) != 9:
        raise ValueError('Номер паспорта должен быть 9 символов')

    phone = phone.replace(' ', '')
    phone = phone.replace('-', '')
    phone = phone.replace('(', '')
    phone = phone.replace(')', '')
    if len(phone) != 13:
        raise ValueError('Номер телефона должен быть 13 символов')

    answer = client.post('registration', {
        'name': name,
        'surname': surname,
        'passport_number': passport_number,
        'passport_id': passport,
        'telephone': phone,
        'password': password
    })

    with open("data/server_config.json", "r") as json_file:
       config = load(json_file)

    jwt_token = answer['data']['JWT']
    config['JWT'] = jwt_token
    config["key"] = answer['data']["key"]
    # Обновляем JWT в клиенте
    client.update_jwt(jwt_token)

    with open("data/server_config.json", "w") as json_file:
        dump(config, json_file)

    client.update_json()

    return True