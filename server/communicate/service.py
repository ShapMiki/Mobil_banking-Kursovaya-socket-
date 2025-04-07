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
                print(data)
            except Exception as e:
                print(f"Error decrypting data: {e}")
                return {"status": 400, "details": "Failed to decrypt data"}


            answer = routers[data['headers']['route']](data)

            encrypted_data = Proccessing.encryption(Proccessing.server_key, answer)
            responce = {'data': encrypted_data}

            return responce


        except Exception as e:
            raise e #TODO: для отладки
            print(f"Unexpected error in post: {e}")
            return {"status": 500, "details": f"Internal server error: {str(e)}"}

    @staticmethod
    def get(data) -> dict:
        try:
            routers = router_dir['get']
            if data['route'] not in routers:
                return {"status": 404, "details": "Route not found"}
            
            answer = {}
            answer['data'] = routers[data['route']](data)
            return answer
        except Exception as e:
            print(f"Error in get: {e}")
            return {"status": 500, "details": f"Internal server error: {str(e)}"}

    @staticmethod
    def security_post(data) -> dict:
        try:
            routers = router_dir['SECURITY_POST']
            if data['route'] not in routers:
                return {"status": 404, "details": "Route not found"}

            # Расшифровка
            try:
                data = Proccessing.decryption(data)
            except Exception as e:
                print(f"Error decrypting data: {e}")
                return {"status": 400, "details": "Failed to decrypt data"}

            # Действие
            try:
                answer = routers[data['route']](data)
                return answer
            except Exception as e:
                print(f"Error processing route: {e}")
                return {"status": 500, "details": f"Error processing request: {str(e)}"}

        except Exception as e:
            print(f"Unexpected error in security_post: {e}")
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
            print(f"ЗАШИФРОВАННО: {data}")
            data = loads(decrypted_data.decode())
            print(f"РАСШИФРОВАННО: {data}")
            return data
        except Exception as e:
            print(f"Ошибка при расшифровке: {str(e)}")
            raise
