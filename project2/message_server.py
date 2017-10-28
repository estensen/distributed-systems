import socket
from threading import Thread, Lock
import sys
import time

NUM_MACHINES = 4
BUFFER_SIZE = 1024

connections = []
for i in range(NUM_MACHINES):
    connections.append(0)
threads = []
listen_threads = []
if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 12345  # Default port if user doesn't enter one


def create_connection(my_port):
    print("Connection thread created with port", my_port)
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # For some reason there's a timeout before sockets can be used again, reuseaddr fixes this problem
    tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        tcp_server_socket.bind(("localhost", my_port))
        tcp_server_socket.listen(1)
        print("Tcpserver calling accept on port ", my_port)
        conn, addr = tcp_server_socket.accept()
        print("Adding to connections the following info: ", connections, addr)
        index = my_port - port
        connections[index] = conn
    finally:
        print("closing 1 time setup socket")
        tcp_server_socket.close()


def listen_for_messages(connection, machine_index):
    '''
    A transaction should not be broadcasted to everyone
    But markers should
    '''
    print("Listening on connection")
    while True:
        data = connection.recv(BUFFER_SIZE)
        if not data or data.decode("utf-8") == "exit":
            print("Clients closed connection")
            for connection in connections:
                connection.close()
            break

        client_messages = data.decode("utf-8")
        client_message_list = client_messages.split("EOM")

        for i in range(len(client_message_list)-1):
            client_message = client_message_list[i]
            client_command = client_message.split(",")[0]
            client_time = client_message.split(",")[1]
            client_port = client_message.split(",")[2]

            print("Client message: \"{}\"".format(client_message))
            print("Client: {} Local time: {} Command: {}".format(client_port, client_time, client_command))

            message_binary = bytes((client_message + "EOM"), encoding="ascii")

            if client_command == "like":
                time.sleep(5)
                for j in range(len(connections)):
                    if connections[j] != connection:
                        mutexes[machine_index].acquire()
                        try:
                            connections[j].send(message_binary)
                        finally:
                            mutexes[machine_index].release()
            elif client_command.split(" ")[0] == "ack":
                source_port = client_command.split(" ")[1]
                # Only send it to the correct source port
                index = int(source_port) - int(port)
                mutexes[machine_index].acquire()
                try:
                    connections[index].send(message_binary)
                finally:
                    mutexes[machine_index].release()
                print("sending {} back ack to {} index {}".format(message_binary.decode("utf-8"),source_port, index))


for i in range(NUM_MACHINES):  # Establish connections to all clients first
    t = Thread(target=create_connection, args=(port+i, ))
    threads.append(t)
    t.start()

for t in threads:  # Clean up threads
    t.join()

for i in range(NUM_MACHINES):  # Establish a listen thread for all clients
    t = Thread(target=listen_for_messages, args=(connections[i], i, ))
    listen_threads.append(t)
    t.start()

for t in threads:  # Clean up threads
    t.join()
