import socket
from config import cluster


def setup(cluster):
    print("Cluster", cluster)
    address_choice = input("Pick an address (A, B or C): ")
    SERVER_ADDR = cluster[address_choice]
    print(SERVER_ADDR)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SERVER_ADDR)
    return sock


def run():
    server = setup(cluster)
    while True:
        data, addr = server.recvfrom(1024)
        print(data)


if __name__ == "__main__":
    run()
