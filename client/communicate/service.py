from communicate.client import client
from json import load, dump
import asyncio

def get_currency():
    answer = client.get('currency_api')
    try:

        currency = answer["data"]

        currency["RUB"]['buy'] *= 0.01
        currency['RUB']['sell'] *= 0.01
        for i in currency:
            currency[i]['buy'] = round(1/currency[i]['buy'], 2)
            currency[i]['sell'] = round(1/currency[i]['sell'], 2)



        print(currency)
        return currency
    except KeyError:
        return answer['details']




def  transfer_service(card_number, adr, sum, transfer_type):
    data = {
        'card_number': card_number,
        "transfer_type": transfer_type,
        'adr': adr,
        'sum': sum
    }
    answer = client.post('transfer_money_api', data)
    return answer["data"]['details']

def create_product(product_type, is_named_product, currency):
    data = {
        'product_type': product_type,
        'is_named_product': is_named_product,
        'currency': currency
    }
    task = client.post('create_product_api', data)
    print(task)

def quit_account():
    with open("data/server_config.json", "r") as json_file:
        config = load(json_file)

    config['JWT'] = None
    config["key"] = None

    with open("data/server_config.json", "w") as json_file:
        dump(config, json_file)

    client.update_json()

def check_auth():
    try:
        answer = client.post('check_auth', {})
    except:
        return False
    try:
         client.update_jwt(answer['data']['JWT'])
    except KeyError:
        return False
    return True

def get_user_data():
    user_data = client.post("get_user_data_api", {})['data']
    #with open("data/user_data.json", "w", encoding="utf-8") as json_file:
    #    dump(user_data, json_file, ensure_ascii=False, indent=4)
    return user_data

async def login(phone, password):
    if not phone or not password:
        raise ValueError('Все поля должны быть заполнены')

    answer =  client.post('login', {
        'telephone': phone,
        'password': password
    })

    with open("data/server_config.json", "r") as json_file:
       config = load(json_file)

    try:
        config['JWT'] = answer['data']['JWT']
        config["key"] = answer['data']["key"]
    except KeyError:
        raise ConnectionAbortedError('Неверный логин или пароль')
    with open("data/server_config.json", "w") as json_file:
        dump(config, json_file)

    client.update_json()

    return True


async def registration(name, surname, passport_number, passport, phone, password):
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

    answer =  client.post('registration', {
        'name': name,
        'surname': surname,
        'passport_number': passport_number,
        'passport_id': passport,
        'telephone': phone,
        'password': password
    })


    with open("data/server_config.json", "r") as json_file:
       config = load(json_file)

    config['JWT'] = answer['data']['JWT']
    config["key"] = answer['data']["key"]

    with open("data/server_config.json", "w") as json_file:
        dump(config, json_file)

    client.update_json()

    return True