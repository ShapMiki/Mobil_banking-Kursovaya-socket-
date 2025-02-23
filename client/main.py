from communicate import service

def main():
    message = {'text': 'hello, world!'}

    sock = socket.socket()
    sock.connect(('localhost', 3333))
    sock.send(dumps(message).encode())

    data = sock.recv(1024)
    sock.close()

    data = loads(data.decode())
    sleep(1)

if __name__ == "__main__":
    main()
