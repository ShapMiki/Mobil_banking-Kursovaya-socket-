import socket

from cryptography.fernet import Fernet
from json import loads, dumps, load, dump
from time import sleep





class Client:
    def __init__(self):
        self.config = {}
        with open("data/server_config.json", "r") as json_file:
            self.config = load(json_file)

        if not self.config["ip"]:
            self.config["ip"] = socket.gethostbyname(socket.gethostname())
            with open("data/server_config.json", "w") as json_file:
                dump(self.config, json_file)

        self.sock = socket.socket()
        print(self.config)
        try:
            self.sock.connect((self.config["host"], self.config["port"]))
        except:
            pass #raise ConnectionError("нет подключения, Попробуйте позже")

        try:
            self.personal_key = self.config["key"].encode()
        except:
            self.personal_key = ""
        self.server_key = self.config["server_key"].encode()


        self.header_pattern = {
            'method': '',
            'route': '',
            'JWT': self.config["JWT"],
            "ip": self.config["ip"],
            "config_version": self.config["config_version"]
        }

    def update_json(self):
        with open("data/server_config.json", "r") as json_file:
            self.config = load(json_file)

    async def reconnect(self):
        try:
            self.sock.connect((self.config["host"], self.config["port"]))
            return True
        except:
             return False

    async def get(self, route, data) -> dict:
        try:
            headers = self.header_pattern.copy()
            headers['method'] = 'get'
            headers['route'] = route
            request = {'headers': headers, 'data': data}
            self.sock.send(dumps(request).encode())
        except:
            if await self.reconnect():
                return await self.get(route, data)
            else:
                raise ConnectionError("нет подключения, Попробуйте позже")

        answer = self.sock.recv(1024)
        answer = loads(answer.decode())

        self.check_answer(answer)
        return answer

    async def post(self, route, data) -> None:
        try:
            data = self.encryption(self.server_key, data)

            headers = self.header_pattern.copy()
            headers['method'] = 'post'
            headers['route'] = route

            request = {'headers': headers, 'data': data}
            self.sock.send(dumps(request).encode())
        except:
            if await self.reconnect():
                return await self.post(route, data)
            else:
                raise ConnectionError("нет подключения")

        answer = self.sock.recv(1024)
        answer = loads(answer.decode())

        if not 200 <= answer["status"] <= 299:
            details = ""
            if answer['details']:
                details = answer['details']
            raise ConnectionError(details)

        answer['data'] = self.decryption(self.server_key, answer['data'])

        return answer


    async def security_post(self, route, data):
        try:
            data = self.encryption(self.personal_key, data)

            headers = self.header_pattern.copy()
            headers['method'] = 'SECURITY_POST'
            headers['route'] = route

            request = {'headers': headers, 'data': data}
            self.sock.send(dumps(request).encode())
        except:
            if await self.reconnect():
                return await self.security_post(route, data)
            else:
                raise ConnectionError("нет подключения")

        answer = self.sock.recv(1024)
        answer = loads(answer.decode())

        if not 200 <= answer["status"] <= 299:
            details = ""
            if answer['details']:
                details = answer['details']
            raise ConnectionError(details)

        answer['data'] = self.decryption(self.personal_key, answer['data'])

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

        return encrypted_data

    def decryption(self, key, data):
        cipher_suite = Fernet(key)
        decrypted_data = cipher_suite.decrypt(data['data'])
        data = {**data, **loads(decrypted_data.decode())}

        return data

    def close_connection(self):
        self.sock.close()


client = Client()