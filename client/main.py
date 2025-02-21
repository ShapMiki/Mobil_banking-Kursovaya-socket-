import socket
from json import dumps
from time import sleep

def main():
    message = {'text': 'hello, world!'}
    while True:
        sock = socket.socket()
        sock.connect(('localhost', 3333))
        sock.send(dumps(message).encode())

        data = sock.recv(1024)
        sock.close()

        print(data, "\n\n")
        sleep(1)

if __name__ == "__main__":
    main()
