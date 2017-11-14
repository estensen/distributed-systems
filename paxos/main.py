import socket
from threading import Thread
from config import cluster
from server import Server

BUFFER_SIZE = 1024
threads = []


def listen_client():
    # Create socket to receive msgs from client
    CLIENT_ADDR = ("localhost", 1337)
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.bind(CLIENT_ADDR)
    print("Client socket created")
    # client_sock.listen(1)
    conn, addr = client_sock.accept()
    while True:
        data, addr = conn.recvfrom(BUFFER_SIZE)
        if not data:
            conn.close()
        msg = data.decode("utf-8")
        print(msg)


def setup(Server):
    # Create socket to receive msgs from other datacenters
    print("Cluster", cluster)
    identifier = input("Pick an address (A, B or C): ")
    server_addr = cluster[identifier]
    server = Server(server_addr)

    return server


def run():
    server = setup(Server)

    while True:
        data = input("Send msg: ")
        server.send_data_to_all(data)

    # Client thread send
    #client_thread = Thread(target=listen_client)
    #threads.append(client_thread)
    #client_thread.start()



if __name__ == "__main__":
    run()
