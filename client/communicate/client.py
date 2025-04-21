import socket
import base64

from cryptography.fernet import Fernet
from json import loads, dumps, load, dump
from time import sleep


class Client:
    def __init__(self):
        self.server_key =b"3nBGTLyXjpz_X-CLFtkEVnm6TdwoX2Igm_3wll1JLek="

        self.config = {}
        with open("data/server_config.json", "r") as json_file:
            self.config = load(json_file)
        if not self.config["ip"]:
            self.config["ip"] = socket.gethostbyname(socket.gethostname())
            with open("data/server_config.json", "w") as json_file:
                dump(self.config, json_file)


        self.sock = socket.socket()
        try:
            self.sock.connect((self.config["host"], self.config["port"]))
        except Exception as e:
            pass

        self.header_pattern = {
            'method': '',
            'route': '',
            'JWT': self.config["JWT"],
            "ip": self.config["ip"],
            "config_version": self.config["config_version"]
        }


    def write_config(self):
        with open("data/server_config.json", "w") as json_file:
            dump(self.config, json_file)


    def update_json(self):
        with open("data/server_config.json", "r") as json_file:
            self.config = load(json_file)


    def update_jwt(self, jwt):
        self.config["JWT"] = jwt
        with open("data/server_config.json", "w") as json_file:
            dump(self.config, json_file)

        self.header_pattern['JWT'] = jwt


    def reconnect(self):
        try:
            self.sock.close()
            self.sock = socket.socket()
            self.sock.connect((self.config["host"], self.config["port"]))
            sleep(0.5)
            return True
        except Exception as e:
             raise e
             return False


    def change_connection(self, ip, port):
        self.config["host"] = ip
        self.config["port"] = port
        self.write_config()


    def get(self, route, data: dict = {"details": "No data"}) -> dict:
        try:
            headers = self.header_pattern.copy()
            headers['method'] = 'get'
            headers['route'] = route
            request = {'headers': headers, 'data': data}
            self.sock.send(dumps(request).encode())
        except OSError as e:
            if self.reconnect():
                return  self.get(route, data)
            else:
                raise OSError("нет подключения, Попробуйте позже")

        answer = self.sock.recv(16384)
        answer = loads(answer.decode())
        print(f"\n\nКлиентом получено(зашифрованно): {answer}")
        if not 200 <= answer["status"] <= 399:
            details = ""
            if answer['details']:
                details = answer['details']
            raise ConnectionError(details)

        self.check_answer(answer)
        return answer


    def post(self, route, data: dict = {"details": "No data"}) -> None:
        try:
            encrypt_data = self.encryption(self.server_key, data)

            headers = self.header_pattern.copy()
            headers['method'] = 'post'
            headers['route'] = route

            request = {'headers': headers, 'data': encrypt_data}

            self.sock.send(dumps(request).encode())
        except OSError as e:
            if self.reconnect():
                return self.post(route, data)
            else:
                raise OSError("нет подключения")

        answer = self.sock.recv(16384)
        answer = loads(answer.decode())

        if not 200 <= answer["status"] <= 399:
            details = ""
            if answer['details']:
                details = answer['details']
            raise ConnectionError(details)

        print(f"\n\nКлиентом получено(зашифрованно): {answer}")
        try:
            answer['data'] = self.decryption(self.server_key, answer['data'])
            print(f"\nКлиентом получено(расшифрованно): {answer}")
        except KeyError:
            answer['data'] = None

        return answer


    def check_answer(self, answer):
        if not 200 <= answer["status"] <= 299:
            details = ""
            if answer['details']:
                details = answer['details']
            raise ConnectionError(details)


    def encryption(self, key, data):
        cipher_suite = Fernet(key)
        json_data = dumps(data).encode()
        encrypted_data = cipher_suite.encrypt(json_data)

        return base64.b64encode(encrypted_data).decode()


    def decryption(self, key, data):
        cipher_suite = Fernet(key)

        encrypted_data = base64.b64decode(data)
        decrypted_data = cipher_suite.decrypt(encrypted_data)

        data =loads(decrypted_data.decode())

        return data


    def close_connection(self):
        self.sock.close()


client = Client()