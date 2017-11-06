import socket
from threading import Thread, Lock
import sys
import time

NUM_MACHINES = 3
BUFFER_SIZE = 1024

mutexes = []
connections = []
for i in range(NUM_MACHINES):
    mutexes.append(Lock())
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


def send_msg_to_client(machine_index, msg):
    command = msg[0]
    src_port = msg[1]
    dst_port = msg[2]
    port_index = int(dst_port) - int(port)
    # This works because the ports are after each other
    msg_binary = bytes((msg + "EOM"), encoding="ascii")

    mutexes.acquire[machine_index].acquire()
    try:
        connections[port_index].send(msg_binary)
    finally:
        mutexes[machine_index].release()
    print("Sending \"{}\" from {} to {}".format(command, src_port, dst_port))


def send_msg_to_all_clients(connection, machine_index, msg):
    command = msg[0]
    src_port = msg[1]

    msg_str = ",".join(msg)
    msg_binary = bytes((msg_str + "EOM"), encoding="ascii")

    for client in connections:
        if client != connection:  # Don't send message to yourself
            mutexes[machine_index].acquire()
            try:
                client.send(msg_binary)
            finally:
                mutexes[machine_index].release()
    print("Sending \"{}\" from {} to all other clients".format(command, src_port))


def parse_msg(connection, machine_index, msg):
    command = msg[0]

    if isinstance(command, int):
        send_msg_to_client(connection, machine_index, msg)
    elif command == "marker":
        send_msg_to_all_clients(connection, machine_index, msg)
    elif command == "snapshot":
        send_msg_to_client(machine_index, msg)
    else:
        command = msg[0]
        print("Command {} not recognized".format(command))


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

        msgs_str = data.decode("utf-8")
        msgs_list = msgs_str.split("EOM")

        for msg_str in msgs_list:
            msg = msg_str.split(",")
            parse_msg(connection, machine_index, msg)


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
