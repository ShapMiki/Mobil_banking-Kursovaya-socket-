import currencyapicom
import schedule


class Currency:
    def __init__(self):
        self.client = currencyapicom.Client('YOUR-API-KEY')
        self.result = {}
    def update(self):
        self.result = self.client.latest()

    def __dir__(self):
        return self.result

currency = Currency()
schedule.every(60).minutes.do(currency.update())