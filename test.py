import multiprocessing as mp
from client.main import main as client_main
from server.main import main as server_main
from time import sleep
from random import randint

def main():
    server = mp.Process(target=server_main)
    server.start()
    sleep(0.5)

    try:
        for _ in range(10):
            clients = []
            count_clients = randint(1, 200)

            for i in range(count_clients):
                clients.append(mp.Process(target=client_main))
                clients[i].start()

            sleep(1)
            for i in range(count_clients):
                clients[i].terminate()
            sleep(0.1)
    except KeyboardInterrupt:
        print("Программа прервана пользователем")
    finally:
        server.terminate()
        for client in clients:
            client.terminate()

if __name__ == "__main__":
    main()