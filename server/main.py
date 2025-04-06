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
    "SECURITY_POST": lambda data: Proccessing.security_post(data)
}

def processing_data(data):
    data = loads(data.decode())
    print(data)

    if not ('headers' in data or 'data' in data):
        return {"status": 400, "details": "bad request"}

    if not data['headers']['config_version'] == settings.config_version:
        return {"status": 421,  'details': "You need to update app"}

    try:
        print(f"\nlog: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')} \nip:{data['headers']['ip']}\n")
    except KeyError:
        return {'status': 403, 'details': 'Forbidden. Need you ip'}

    try:
        answer = functions[data['headers']['method']](data)
    except KeyError:
        return {"status": 404, 'details': 'Method not found'}
    except Exception as e:
        print(f"Error processing request: {e}")
        return {"status": 500, "details": f"Internal Server Error: {str(e)}"}

    if not 'status' in answer.keys():
        answer['status'] = 200

    answer = dumps(answer).encode()
    return answer



def handle_client(conn):
    conn.settimeout(CONNECTION_TIMEOUT)
    while True:
        try:
            data = conn.recv(2048)

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
            raise e
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