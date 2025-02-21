import socket


def main():
    sock = socket.socket()
    sock.bind(('localhost', 3333))
    sock.listen(1)

    while True:
        conn, addr = sock.accept()
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.send(data)
            print(data)
        conn.close()


if __name__ == "__main__":
    main()