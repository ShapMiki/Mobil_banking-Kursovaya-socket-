import socket

from cryptography.fernet import Fernet
from json import loads, dumps
from time import sleep



HOST = "localhost"
PORT = 3333
key = b'M95xDbhZivBW2dvs00BSE7WPgh6c2oEXIo7EX5NUizc='


class Client:
    def __init__(self):
        self.sock = socket.socket()
        self.sock.connect((HOST, PORT))

        self.cipher_suite = Fernet(key)
        self.header_pattern = {
            'method': '',
            'route': ''
        }

    def reconnect(self):
        try:
            self.sock.connect((HOST, PORT))
            return True
        except:
             return False


    def post(self, route, data) -> None:
        try:
            data = self.encryption(data)

            headers = self.header_pattern.copy()
            headers['method'] = 'post'
            headers['route'] = route

            message = [headers, data]

            self.sock.send(data)
        except:
            if self.reconnect():
                return self.post(data)
            else:
                raise ConnectionError("нет подключения")

        answer = self.sock.recv(1024)
        answer = loads(answer.decode())

        if not 200 <= answer["status"] <= 299:
            details = ""
            if answer['details']:
                details = answer['details']
            raise ConnectionError(details)

        return(answer)


    def security_post(self, data):
        try:
            data = self.encryption(data)
            data['method'] = 'SECURITY_POST'
            self.sock.send(data)
        except:
            if self.reconnect():
                return self.security_post(data)
            else:
                raise ConnectionError("нет подключения")

        answer = self.sock.recv(1024)
        answer = loads(answer.decode())

        self.check_answer(answer)
        if answer['data']:
            answer = self.decryption(answer[data])

        return answer

    def get(self, data) -> dict:
        try:
            data['method'] = 'get'
            self.sock.send(dumps(data).encode())
        except:
            if self.reconnect():
                return self.get(data)
            else:
                raise ConnectionError("нет подключения")

        answer = self.sock.recv(1024)
        answer = loads(answer.decode())

        self.check_answer(answer)
        return answer

    def check_answer(self, answer):
        if not 200 <= answer["status"] <= 299:
            details = ""
            if answer['details']:
                details = answer['details']
            raise ConnectionError(details)

    def encryption(self, data):
        json_data = dumps(data).encode()
        encrypted_data = self.cipher_suite.encrypt(json_data)

        return encrypted_data

    def decryption(self, data):
        if not data['encrypt']:
            return data

        decrypted_data = self.cipher_suite.decrypt(data['data'])
        data = { **data, **loads(decrypted_data.decode())}

        return data

    def close_connection(self):
        self.sock.close()