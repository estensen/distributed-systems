import socket
import sys
from threading import Thread
from multiprocessing import Lock
from random import randint
import time #time.sleep

local_time = 0
host = "localhost"
port = int(sys.argv[1])
process_id = port
BUFFER_SIZE = 1024
NUM_MACHINES = 4
threads = []
blocked_processes=[]
want_resource = False
want_resource_message = ""
mutex = Lock()

like_mutex = Lock()

tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpClient.connect((host, port))


def update_local_time(received_time):
    return max(local_time, received_time)


def read_post():
    while (True):
        like_mutex.acquire()
        try:
            with open("likes.txt", "r") as f:
                result = f.read()
                if not result:
                    f.close()
                    time.sleep(0.3)
                    continue
                else:
                    current_likes = int(result)
                    f.close()
                    break
        finally:
            like_mutex.release()
    return current_likes


def like_post():
    # TODO: Make sure read and write are atomic
    while True:
        like_mutex.acquire()
        try:
            with open("likes.txt", "r+") as f:
                result = f.read()
                if not result:
                    f.close()
                    time.sleep(0.3)
                    continue
                else:
                    current_likes = int(result)
                    print("Current likes:", current_likes)
                    new_likes = current_likes + 1
                    f.seek(0)
                    f.truncate()
                    f.write(str(new_likes))
                    print("New likes:", new_likes)
                    break
        finally:
                like_mutex.release()


def return_true_if_earlier(my_request_with_eom, other_request_with_eom):
    my_request = my_request_with_eom.replace("EOM","")
    other_request = other_request_with_eom.replace("EOM","")
    print("Comparing my request: {}, other request: {}".format(my_request, other_request))
    my_time = int(my_request.split(",")[1])
    other_time = int(other_request.split(",")[1])
    if my_time < other_time:
        return True
    elif my_time > other_time:
        return False
    else:
        my_id = int(my_request.split(",")[2])
        other_id = int(other_request.split(",")[2])
        if my_id < other_id:
            return True
        else:
            return False


def send_messages(connection):
    # Message format: "<command>,<port>,<local_time>
    while True:
        user_input = input("Available commands: read, like, or exit\n")

        global local_time
        local_time += 1
        message_str = user_input + ",{},{}EOM".format(local_time, port)  # EOM (end of message) splits messages
        message_binary = bytes(message_str, encoding="ascii")

        print("Local time:", local_time)
        if user_input == "test":
            mutex.acquire()
            try:
                connection.send(message_binary)
            finally:
                mutex.release()
            mutex.acquire()
            try:
                connection.send(message_binary)
            finally:
                mutex.release()

        elif user_input == "read":
            print ("user called", user_input)
            print("\"TESTCASE CONTENT\" Likes: {}".format(read_post()))
            mutex.acquire()
            try:
                connection.send(message_binary)
            finally:
                mutex.release()
        elif user_input == "like":
            print("user called", user_input)
            mutex.acquire()
            try:
                connection.send(message_binary)
            finally:
                mutex.release()
            global want_resource
            global want_resource_message
            want_resource = True
            want_resource_message = message_str
        elif user_input == "exit":
            mutex.acquire()
            try:
                connection.send(bytes("exit", encoding="ascii"))
            finally:
                mutex.release()
            connection.close()
            break
        else:
            print("unrecognized command, please try read, like, or exit")


def listen_for_messages(connection):
    acks = set()  # Can currently only handle one lock request from each machine at a time.
    while True:
        message_binary = connection.recv(BUFFER_SIZE)
        message_str = message_binary.decode("utf-8")

        if not message_str:
            connection.close()
            break

        message_list = message_str.split("EOM")

        for i in range(len(message_list)-1):
            individual_message = message_list[i]
            message_arr = individual_message.split(",")

            if message_arr[0] == "exit":
                connection.close()
                break

            global local_time
            global want_resource
            global want_resource_message
            global blocked_processes
            # Uncomment if local time increases when sending acks
            # local_time += 1
            local_time = update_local_time(int(message_arr[1]))
            print("Local time: ", local_time)

            if message_arr[0] == "like":
                request_source_port = message_arr[2]
                print("Machine {} wants the lock".format(request_source_port))
                response_str = "ack {},{},{}EOM".format(request_source_port,local_time, port)
                response_binary = bytes(response_str, encoding="ascii")

                if want_resource:
                    my_priority = return_true_if_earlier(want_resource_message,message_str)
                    if my_priority:
                        print("MY PROCESS IS EARLIER, BLOCKING")
                        blocked_processes.append(response_binary)
                    else:
                        mutex.acquire()
                        try:
                            connection.send(response_binary)
                        finally:
                            mutex.release()
                else:
                    mutex.acquire()
                    try:
                        connection.send(response_binary)
                    finally:
                        mutex.release()

            if message_arr[0].split(" ")[0] == "ack":
                # TODO: Don't allow like_post() to be called if an ack that was not warranted is received.
                print("Ack received from {}".format(message_arr[2]))
                acks.add(message_arr[2])
            if len(acks) == NUM_MACHINES - 1:
                print("LOCK ACQUIRED!")
                like_post()
                acks = set()
                want_resource = False
                want_resource_message = ""
                for response_binary in blocked_processes:
                    mutex.acquire()
                    try:
                        connection.send(response_binary)
                    finally:
                        mutex.release()
                blocked_processes = []


t = Thread(target=send_messages, args=(tcpClient, ))
threads.append(t)
t.start()

t = Thread(target=listen_for_messages, args=(tcpClient, ))
threads.append(t)
t.start()

for t in threads:
    t.join()
tcpClient.close()
