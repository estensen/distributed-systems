import socket
import sys
from threading import Thread


local_time = 0
host = "localhost"
port = int(sys.argv[1])
BUFFER_SIZE = 1024
NUM_MACHINES = 2
threads = []

tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpClient.connect((host, port))


def update_local_time(received_time):
    return max(local_time, received_time)


def like_post():
    # TODO: Make sure read and write are atomic
    with open("likes.txt", "r+") as f:
        current_likes = int(f.read())
        print("Current likes:",current_likes)
        new_likes = current_likes + 1
        f.seek(0)
        f.truncate()
        f.write(str(new_likes))
    f.close()


def send_messages(connection):
    # Message format: "<command>,<port>,<local_time>
    while True:
        user_input = input("Please enter a message to send to all clients:\n")
        global local_time
        local_time += 1
        message_str = user_input + ",{},{}".format(local_time, port)
        message_binary = bytes(message_str, encoding="ascii")
        connection.send(message_binary)
        if message_str == "exit":
            connection.close()
            break


def listen_for_messages(connection):
    acks = set()  # Can currently only handle one lock request from each machine at a time.
    while True:
        message_binary = connection.recv(BUFFER_SIZE)
        message_str = message_binary.decode("utf-8")
        message_arr = message_str.split(",")
        global local_time
        local_time += 1
        local_time = update_local_time(int(message_arr[1]))
        print("Local time: ", local_time)

        if message_arr[0] == "lock":
            print("Machine {} wants the lock".format(message_arr[2]))
            response_str = "ack,{},{}".format(local_time, port)
            response_binary = bytes(response_str, encoding="ascii")
            connection.send(response_binary)

        if message_arr[0] == "ack":
            # TODO: Don't allow like_post() to be called if an ack that was not warranted is received.
            print("Ack received from {}".format(message_arr[2]))
            acks.add(message_arr[1])

        if not message_arr:
            print("Server closed connection")
            connection.close()
            break
        print("Received message \"{}\"".format(message_str))

        if len(acks) == NUM_MACHINES - 1:
            print("Lock acquired!")
            like_post()
            acks = set()


t = Thread(target=send_messages, args=(tcpClient, ))
threads.append(t)
t.start()

t = Thread(target=listen_for_messages, args=(tcpClient, ))
threads.append(t)
t.start()

for t in threads:
    t.join()
tcpClient.close()
