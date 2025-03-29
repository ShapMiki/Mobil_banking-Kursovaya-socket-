import socket
from threading import Thread
from json import dumps, loads
from datetime import datetime

from communicate.service import Proccessing
from config import settings



HOST = "localhost"
PORT = 3333
CONNECTION_TIMEOUT = 30

functions = {
    "get": lambda: Proccessing.get,
    "post": lambda: Proccessing.post,
    "SECURITY_POST": lambda: Proccessing.security_post,
}

def processing_data(data):
    data = loads(data.decode())

    if not ('headers' in data or 'data' in data):
        return {"status": 400, "details": "bad request"}

    if not data['headers']['config_version'] == settings.config_version:
        return {"status": 421,  'details': "You need to update app"}

    try:
        print(f"\nlog: {datetime.now().strftime('%h:%m:%s %d:%m:%Y')} \nip:{data['headers']['ip']}\n")
    except KeyError:
        return {'status': 403, 'details': 'Forbidden. Need you ip'}

    try:
        answer = functions[data['headers']['method']](data)                     #Испольнение запроса
    except KeyError:
        answer = {"status": 404, 'details': 'not found'}
    except Exception as e:
        answer = {"status":500, "details": f"internal Serverv Error: {e}"}

    answer = dumps(answer).encode()
    return answer


def handle_client(conn):
    conn.settimeout(CONNECTION_TIMEOUT)
    while True:
        try:
            data = conn.recv(1024)

            if not data:
                continue

            conn.settimeout(CONNECTION_TIMEOUT)
            answer = processing_data(data)
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
            answer  = {"status": 500, "details": str(e)}
            conn.send(dumps(answer).encode())
            break

    conn.close()


def main():
    sock = socket.socket()
    sock.bind((HOST, PORT))
    sock.listen(50)

    while True:
        conn, addr = sock.accept()

        client_thread = Thread(target=handle_client, args=(conn,))
        client_thread.start()

if __name__ == "__main__":
    main()