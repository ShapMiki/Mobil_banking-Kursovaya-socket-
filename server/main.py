import socket
from threading import Thread
from json import dumps, loads
from datetime import datetime
from communicate.service import Proccessing

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

    try:
        answer = functions[data['headers']['method']](data)
    except KeyError:
        answer = {"status": 404, 'details': 'not found'}
    except:
        answer = {"status":500, "details": "internal Serverv Error"}

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