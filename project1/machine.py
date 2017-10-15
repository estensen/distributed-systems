import socket
import sys
from threading import Thread, Lock
from random import randint
import time #time.sleep

local_time = 0
host = "localhost"
port = int(sys.argv[1])
process_id = port #port is also the process id for the machine
BUFFER_SIZE = 1024
NUM_MACHINES = 4
threads = []
blocked_processes=[]
want_resource = False
want_resource_message = ""
mutex = Lock()

tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpClient.connect((host, port))


def update_local_time(received_time):
    return max(local_time, received_time)

def read_post():
    with open("likes.txt", "r") as f:
        current_likes = int(f.read())
    f.close()
    return current_likes

def like_post():
    # TODO: Make sure read and write are atomic
    with open("likes.txt", "r+") as f:
        current_likes = int(f.read())
        print("Current likes:",current_likes)
        new_likes = current_likes + 1
        f.seek(0)
        f.truncate()
        f.write(str(new_likes))
        print("New likes:",new_likes)
    f.close()

#returns true if my process should go first
def return_true_if_earlier(my_request_with_EOM, other_request_with_EOM):
    my_request = my_request_with_EOM.replace("EOM","");
    other_request = other_request_with_EOM.replace("EOM","")
    print("Comparing my request: {}, other request: {}".format(my_request, other_request))
    my_time = int(my_request.split(",")[1])
    other_time = int(other_request.split(",")[1])
    if (my_time < other_time):
        return True
    elif (my_time > other_time):
        return False
    else:
        my_id = int(my_request.split(",")[2])
        other_id = int(other_request.split(",")[2])
        if (my_id < other_id):
            return True
        else:
            return False

def send_messages(connection):
    # Message format: "<command>,<port>,<local_time>
    while True:
        user_input = input("Available commands: read, like, or exit\n")
        #Please enter a message to send to all clients:\n")

        
        global local_time

        local_time += 1
        #construct message
        message_str = user_input + ",{},{}EOM".format(local_time, port) #split messages by EOM: end of message
        message_binary = bytes(message_str, encoding="ascii")


        print( "Local time:", local_time) 
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
            print("TESTCASE CONTENT Like:%d" %read_post())
            mutex.acquire()
            try:
                connection.send(message_binary)
            finally:
                mutex.release()
        elif user_input == "like":
            print ("user called", user_input)
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
            print ("unrecognized command, please try read, like, or exit")

def listen_for_messages(connection):
    acks = set()  # Can currently only handle one lock request from each machine at a time.
    while True:
        message_binary = connection.recv(BUFFER_SIZE)
        message_str = message_binary.decode("utf-8")

        if not message_str:
            connection.close()
            break

        message_list = message_str.split("EOM")
        #print ("message list:", message_list)

        for i in range(len(message_list)-1):
            individual_message = message_list[i]
            message_arr = individual_message.split(",")

            #close the connection if server disconnects
            if message_arr[0] == "exit":
                connection.close()
                break

            global local_time
            global want_resource
            global want_resource_message
            local_time += 1
            local_time = update_local_time(int(message_arr[1]))
            print("Local time: ", local_time)

            if message_arr[0] == "like":
                request_source_port = message_arr[2]
                print("Machine {} wants the lock".format(request_source_port))

                #construct return message
                response_str = "ack {},{},{}EOM".format(request_source_port,local_time, port)
                response_binary = bytes(response_str, encoding="ascii")

                #if i want resource, check who blocks who
                if (want_resource):
                    my_priority = return_true_if_earlier(want_resource_message,message_str)
                    if (my_priority): #block the other message
                        print("MY PROCESS IS EALIER, BLOCKING")
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

            #print(message_arr)
            if message_arr[0].split(" ")[0] == "ack":
                # TODO: Don't allow like_post() to be called if an ack that was not warranted is received.
                print("Ack received from {}".format(message_arr[2]))
                acks.add(message_arr[2])

            #print("Received message \"{}\"".format(message_str))

            #print("acks list: {}".format(acks))

            if len(acks) == NUM_MACHINES - 1:
                print("LOCK ACQUIRED!!!")
                like_post()
                #reset state variables
                acks = set()
                want_resource = False
                want_resource_message = ""
                #unblock blocked processes
                #print ("unblocking processes", blocked_processes)
                for response_binary in blocked_processes:
                    mutex.acquire()
                    try:
                        connection.send(response_binary)
                    finally:
                        mutex.release()

t = Thread(target=send_messages, args=(tcpClient, ))
threads.append(t)
t.start()

t = Thread(target=listen_for_messages, args=(tcpClient, ))
threads.append(t)
t.start()

for t in threads:
    t.join()
tcpClient.close()
