import socket
from threading import Thread 
import sys


connections = []
threads = [] # Threads that create the initial socket connections
listen_threads = [] # Threads to listen to client threads, 1 thread for each client
if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 12345  # Default port if user doesn't enter one
NUM_CLIENTS = 2

BUFFER_SIZE = 1024


def create_connection(port):
    print("connection thread created with port", port)
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # For some reason there's a timeout before sockets can be used again, reuseaddr fixes this problem
    tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        tcp_server_socket.bind(("localhost", port))
        tcp_server_socket.listen(1)
        print("tcpserver calling accept on port ", port)
        conn, addr = tcp_server_socket.accept()
        print("appending to connections the following info: ", connections, addr)
        connections.append(conn)
    finally:
        print("closing setup socket (either executed properly or timed out")
        tcp_server_socket.close()


def listen_for_messages(connection):
    print("Listening on connection")
    while True:
        data = connection.recv(BUFFER_SIZE)
        if not data or data == "exit":  # If data is empty, it means client closed connection
            print("Client closed connection")
            connection.close()
            connections.remove(connection)
            print("Updated connection list:")
            break

        print("Received data", data.decode("utf-8"))
        # Send the data to all the other clients
        for other_connection in connections:
            if other_connection != connection:
                other_connection.send(data)


for i in range(NUM_CLIENTS):  # Establish connections to all clients first
    t = Thread(target=create_connection, args=(port+i, ))
    threads.append(t)
    t.start()

for t in threads:  # Clean up threads
    t.join()

for i in range(NUM_CLIENTS):  # Establish a listen thread for all clients
    t = Thread(target=listen_for_messages, args=(connections[i], ))
    listen_threads.append(t)
    t.start()

for t in threads:  # Clean up threads
    t.join()

