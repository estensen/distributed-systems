import socket
from threading import Thread
from config import cluster
from server import Server

BUFFER_SIZE = 1024
threads = []

def setup(Server):
    # Create socket to receive msgs from other datacenters
    print("Cluster", cluster)
    identifier = input("Pick an address (A, B or C): ")
    server_addr = cluster[identifier]
    server = Server(server_addr)

    return server


def run():
    server = setup(Server)

    #while True:
    #    data = input("Send msg: ")
    #    server.send_data_to_all(data)


if __name__ == "__main__":
    run()
