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


def listen_datacenters(sock):
    while True:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        msg = data.decode("utf-8")
        print(msg)


def send_data(sock):
    data = "Hello"
    msg = bytes(data, encoding="ascii")
    sock.sendto(msg, cluster['B'])


def setup(cluster):
    # Create socket to receive msgs from other datacenters
    print("Cluster", cluster)
    address_choice = input("Pick an address (A, B or C): ")
    SERVER_ADDR = cluster[address_choice]
    print(SERVER_ADDR)
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind(SERVER_ADDR)
    print("Server socket created")

    return server_sock


def run():
    server_sock = setup(cluster)

    # Server listen thread
    server_listen_thread = Thread(target=listen_datacenters, args=(server_sock, ))
    threads.append(server_listen_thread)
    server_listen_thread.start()

    # Server send thread
    server_send_thread = Thread(target=send_data, args=(server_sock, ))
    threads.append(server_send_thread)
    server_send_thread.start()

    # Client thread send
    client_thread = Thread(target=listen_client)
    threads.append(client_thread)
    client_thread.start()



if __name__ == "__main__":
    run()
