from json import load, dump

class Credit_info:
    def __init__(self):
        self.data = {}
        self.update_data()

    def update_data(self):
        with open("data/credit_info.json", "r", encoding="UTF-8") as json_file:
            self.data = load(json_file)

class Entity_data:
    def __init__(self):
        self.data = {}
        self.update_data()

    def update_data(self):
        with open("data/entity_data.json", "r", encoding="UTF-8") as json_file:
            self.data = load(json_file)

entity_data = Entity_data()
credit_info = Credit_info()