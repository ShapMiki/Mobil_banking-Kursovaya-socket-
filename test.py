import multiprocessing as mp
from client.main import main as client_main
from server.main import main as server_main
from time import sleep

def main():
    client = mp.Process(target=client_main)
    server = mp.Process(target=server_main)

    server.start()
    sleep(1)
    client.start()


if __name__ == "__main__":
    main()
