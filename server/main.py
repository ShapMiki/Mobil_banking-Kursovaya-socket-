import socket
from threading import Thread
from json import dumps, loads


def processing_data(data):
    data = loads(data.decode())
    ###НУжно сделать распределение по функциям
    answer = {"status": 200}
    ###
    answer = dumps(answer).encode()
    return answer

def handle_client(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            break

        answer = processing_data(data)
        conn.send(answer)

        print(data)
    conn.close()


def main():
    sock = socket.socket()
    sock.bind(('localhost', 3333))
    sock.listen(5)

    while True:
        conn, addr = sock.accept()
        client_thread = Thread(target=handle_client, args=(conn,))
        client_thread.start()

if __name__ == "__main__":
    main()