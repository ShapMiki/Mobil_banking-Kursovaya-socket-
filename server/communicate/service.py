from json import loads, dumps

from communicate.route import router_dir


class Proccessing:
    @staticmethod
    def post(cls, data) -> dict:
        routers = router_dir['post']
        if data['route'] not in routers:
            return {"status": 404, "details": "Route not found"}
        pass

        #TODO: сделать расшифровку, обработку  данных, шифрование и отправка ответа по ключу сервера


    @staticmethod
    def get(cls, data) ->dict:
        routers = router_dir['get']
        if data['route'] not in routers:
            return {"status": 404, "details": "Route not found"}

        answer = routers[data['route']](data)

        return answer

    #TODO: Написать отдельный метод для регистрации и авторизации, обновления jwt

    @staticmethod
    def security_post(cls, data) -> dict:
        routers = router_dir['SECURITY_POST']
        if data['route'] not in routers:
            return {"status": 404, "details": "Route not found"}

        # TODO: сделать расшифровку, обработку  данных, шифрование и отправка ответа по ключу пользователя

        #расшифровка
        data = cls.decryption(data)
        #действие
        answer = routers[data['route']](data)
        #шифровка
        #!!!!!!!!
        return answer

    @staticmethod
    def auth_post(cls, data):
        pass

    @staticmethod
    def encryption(self, data):
        pattern = {
            'method': '',
            'encrypt': True,
            'data': ''
        }

        #TODO: разобраться, что за гауно
        json_data = dumps(data).encode()
        encrypted_data = self.cipher_suite.encrypt(json_data)

        return encrypted_data

    @staticmethod
    def decryption(self, data):
        if not data['encrypt']:
            return data

        decrypted_data = self.cipher_suite.decrypt(data['data'])
        data = { **data, **loads(decrypted_data.decode())}

        return data
