from json import loads, dumps
from cryptography.fernet import Fernet
import base64

from communicate.route import router_dir
from config import settings



class Proccessing:
    server_key = settings.secret_server_key
    @staticmethod
    def post(data) -> dict:
        routers = router_dir['post']
        if data['headers']['route'] not in routers:
            return {"status": 404, "details": "Route not found"}
        data['data'] = Proccessing.decryption(Proccessing.server_key, data['data'])
        print(data)
        answer = routers[data['headers']['route']](data)

        responce = {}
        responce['data'] = Proccessing.encryption(Proccessing.server_key, answer)
        return responce

    @staticmethod
    def get(data) ->dict:
        routers = router_dir['get']
        if data['route'] not in routers:
            return {"status": 404, "details": "Route not found"}
        answer = {}
        answer['data'] = routers[data['route']](data)

        return answer


    @staticmethod
    def security_post(data) -> dict:
        routers = router_dir['SECURITY_POST']
        if data['route'] not in routers:
            return {"status": 404, "details": "Route not found"}

        # TODO: сделать расшифровку, обработку  данных, шифрование и отправка ответа по ключу пользователя

        #расшифровка
        data = Proccessing.decryption(data)
        #действие
        answer = routers[data['route']](data)
        #шифровка
        #!!!!!!!!
        return answer

    @staticmethod
    def encryption(key, data):
        cipher_suite = Fernet(key)
        json_data = dumps(data).encode()
        encrypted_data = cipher_suite.encrypt(json_data)
        return base64.b64encode(encrypted_data).decode()

    @staticmethod
    def decryption(key, data):
        cipher_suite = Fernet(key)
        try:
            encrypted_data = base64.b64decode(data)
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            print(f"ЗАШИФРОВАННО: {data}")
            data = loads(decrypted_data.decode())
            print(f"РАСШИФРОВАННО: {data}")
            return data
        except Exception as e:
            print(f"Ошибка при расшифровке: {str(e)}")
            raise e
