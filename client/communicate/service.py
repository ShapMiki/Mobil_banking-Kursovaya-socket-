from communicate.client import client
from json import load, dump



async def login(phone, password):
    answer = await client.post('login', {
        'phone': phone,
        'password': password
    })

    with open("data/server_config.json", "r") as json_file:
       config = load(json_file)

    try:
        config['JWT'] = answer['JWT']
        config["key"] = answer["key"]
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
        raise ValueError('Номер паспорта должен быть 14 символов')
    if len(passport_number) != 9:
        raise ValueError('Номер паспорта должен быть 9 символов')

    phone = phone.replace(' ', '')
    phone = phone.replace('-', '')
    phone = phone.replace('(', '')
    phone = phone.replace(')', '')
    if len(phone) != 13:
        raise ValueError('Номер телефона должен быть 13 символов')

    answer = await client.post('registration', {
        'name': name.get(),
        'surname': surname.get(),
        'passport_number': passport_number.get(),
        'passport': passport.get(),
        'phone': phone.get(),
        'password': password.get()
    })


    with open("data/server_config.json", "r") as json_file:
       config = load(json_file)

    config['JWT'] = answer['JWT']
    config["key"] = answer["key"]

    with open("data/server_config.json", "w") as json_file:
        dump(config, json_file)

    client.update_json()

    return True