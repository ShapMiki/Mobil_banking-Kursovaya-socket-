#docker save -o shadypay.tar shadypay:latest
import socket
from threading import Thread
from json import dumps, loads
from datetime import datetime

from communicate.service import Proccessing
from config import settings



HOST = settings.host
PORT = int(settings.port)
CONNECTION_TIMEOUT = 600

functions = {
    "get": lambda data: Proccessing.get(data),
    "post": lambda data: Proccessing.post(data),
}

def processing_data(data):
    try:
        data = loads(data.decode())
        print(data)

        if not ('headers' in data or 'data' in data):
            return  dumps({"status": 400, "details": "bad request"}).encode()

        if not data['headers']['config_version'] == settings.config_version:
            return  dumps({"status": 421,  'details': "You need to update app"}).encode()

        try:
            print(f"\nlog: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')} \nip:{data['headers']['ip']}\n")
        except KeyError:
            return  dumps({'status': 403, 'details': 'Forbidden. Need you ip'}).encode()

        try:
            answer = functions[data['headers']['method']](data)
        except KeyError as e:
            raise e  # TODO: для отладки
            return dumps( {"status": 404, 'details': 'Method not found'}).encode()
        except Exception as e:
            raise e  # TODO: для отладки
            print(f"Error processing request: {e}")
            return dumps( {"status": 501, "details": f"Internal Server Error: {str(e)}"}).encode()
    except Exception as e:
        print(f"log {datetime.now()}: {e}")
        raise e #TODO: для отладки
        return dumps({"status": 400, "details": "Bad request"}).encode()


    if not 'status' in answer.keys():
        answer['status'] = 200

    answer = dumps(answer).encode()
    return answer



def handle_client(conn):
    conn.settimeout(CONNECTION_TIMEOUT)
    while True:
        try:
            data = conn.recv(16384)

            if not data:
                continue

            conn.settimeout(CONNECTION_TIMEOUT)
            answer = processing_data(data)
            print("23432",answer)
            conn.send(answer)

        except socket.timeout:
            print(f"log {datetime.now()}: тайм-аут соединения")
            break

        except ConnectionResetError:
            print(f"log {datetime.now()}: подключение неожиданно разорвано")
            conn.close()
            break
        except OSError:
            print(f"log {datetime.now()}: соединение закрыто")
            conn.close()
            break

        except Exception as e:
            print(e)
            answer  = {"status": 500, "details": str(e)}
            conn.send(dumps(answer).encode())
            break

    conn.close()


def main():
    print("Сервер запущен")
    sock = socket.socket()

    print(f"HOST: {HOST}, PORT: {PORT}")
    sock.bind((HOST, PORT))

    sock.listen(50)

    while True:
        conn, addr = sock.accept()

        client_thread = Thread(target=handle_client, args=(conn,))
        client_thread.start()

if __name__ == "__main__":
    main()