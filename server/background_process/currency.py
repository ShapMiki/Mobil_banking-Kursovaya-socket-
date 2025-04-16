import currencyapicom
import schedule
from random import randrange
from json import load, dump
import threading
import time

from config import settings
from datetime import datetime, timedelta


class Currency:
    def __init__(self):
        self.client = currencyapicom.Client(settings.currencyapicom_api_key)
        self.currency = {}
        self.shd = 0.001
        self.get_shd()
        schedule.every(60).minutes.do(self.update)
        schedule.every(1).minutes.do(self.calculate_shd)
        self.update()
        self.start_scheduler()

    def update(self):
        result = {}
        with open("data/currency.json", "r") as json_file:
            result.update(load(json_file))

        if datetime.fromisoformat(result['last_update']) < datetime.now() - timedelta(hours=24):
            currency = self.client.latest(currencies=['USD', 'EUR', 'RUB', 'BYN'], base_currency='BYN')

            self.currency ={
                'USD': currency['data']['USD']['value'],
                'EUR': currency['data']['EUR']['value'],
                'RUB': currency['data']['RUB']['value'],
                'BYN': currency['data']['BYN']['value'],
            }
            result={
                'last_update': datetime.now().isoformat(),
            }
            result.update(self.currency)
            print(result) # TODO: для отладки
            with open("data/currency.json", "w") as json_file:
                dump(result, json_file)
        else:
            with open("data/currency.json", "r") as json_file:
                self.currency = load(json_file)
                self.currency.pop('last_update')
                print(self.currency) # TODO: для отладки

    def save_shd(self):
        data = {"shd": self.shd}
        with open("data/shd.json", "w", encoding="UTF-8") as json_file:
            dump(data, json_file)

    def get_shd(self):
        try:
            with open("data/shd.json", "r", encoding="UTF-8") as json_file:
                data = load(json_file)
                self.shd = data['shd']
        except FileNotFoundError:
            self.shd = 0.001
            self.save_shd()

    def calculate_shd(self):
        big_game = randrange(0,20,1)
        if big_game == 1:
            procent = randrange(-200, 200)/100
        else:
            procent = randrange(-100, 100, )/1000

        if self.shd < 0.0001:
            procent = abs(procent)

        self.shd += self.shd * procent
        self.save_shd()

    def to_dict(self) -> dict:
        answer = {
            "USD":{
                "buy": self.currency['USD']*1.01,
                "sell": self.currency['USD']*0.99
            },
            "EUR":{
                "buy": self.currency['EUR']*1.01,
                "sell": self.currency['EUR']*0.99
            },
            "RUB":{
                "buy": self.currency['RUB']*1.01,
                "sell": self.currency['RUB']*0.99
            },
            "BYN":{
                "buy": self.currency['BYN']*1.01,
                "sell": self.currency['BYN']*0.99
            },
            "SHD":{
                "buy": self.shd*1.01,
                "sell": self.shd*0.99
            }
        }
        return answer

    def start_scheduler(self):
        def run():
            while True:
                schedule.run_pending()
                time.sleep(1)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

currency = Currency()
