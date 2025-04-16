from json import loads, dumps
from cryptography.fernet import Fernet
import base64

from communicate.route import router_dir
from config import settings



class Proccessing:
    server_key = settings.secret_server_key
    @staticmethod
    def post(data) -> dict:
        try:
            routers = router_dir['post']
            if data['headers']['route'] not in routers:
                return {"status": 404, "details": "Route not found"}

            # Расшифровываем данные
            try:
                data['data'] = Proccessing.decryption(Proccessing.server_key, data['data'])
                print(data) # TODO: для отладки
            except Exception as e:
                print(f"Error decrypting data: {e}")
                return {"status": 400, "details": "Failed to decrypt data"}


            answer = routers[data['headers']['route']](data)

            encrypted_data = Proccessing.encryption(Proccessing.server_key, answer)
            responce = {'data': encrypted_data}

            if  'details'  and 'status' in answer.keys():
                responce["status"] = answer['status']
                responce['details'] = answer['details']

            return responce


        except Exception as e:
            raise e #TODO: для отладки
            print(f"Unexpected error in post: {e}")
            return {"status": 500, "details": f"Internal server error: {str(e)}"}

    @staticmethod
    def get(data) -> dict:
        try:
            routers = router_dir['get']
            print(data) # TODO: для отладки
            if data['headers']['route'] not in routers:
                return {"status": 404, "details": "Route not found"}
            
            answer = {}
            answer.update(routers[data['headers']['route']](data))

            responce = {'data': answer}

            if 'details' and 'status' in answer.keys():
                responce["status"] = answer['status']
                responce['details'] = answer['details']

            return responce
        except Exception as e:
            print(f"Error in get: {e}")
            raise e # TODO: для отладки
            return {"status": 500, "details": f"Internal server error: {str(e)}"}

    @staticmethod
    def encryption(key, data):
        try:
            cipher_suite = Fernet(key)
            json_data = dumps(data).encode()
            encrypted_data = cipher_suite.encrypt(json_data)
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            print(f"Error in encryption: {e}")
            raise

    @staticmethod
    def decryption(key, data):
        try:
            cipher_suite = Fernet(key)
            encrypted_data = base64.b64decode(data)
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            print(f"ЗАШИФРОВАННО: {data}") # TODO: для отладки
            data = loads(decrypted_data.decode())
            print(f"РАСШИФРОВАННО: {data}") # TODO: для отладки
            return data
        except Exception as e:
            print(f"Ошибка при расшифровке: {str(e)}")
            raise
