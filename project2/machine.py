import socket
import sys
from threading import Thread
from multiprocessing import Lock
from random import randint
import time

local_account_balance = 1000
host = "localhost"
port = int(sys.argv[1])
process_id = port
BUFFER_SIZE = 1024
NUM_MACHINES = 4
threads = []
blocked_processes=[]

tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpClient.connect((host, port))


def update_local_time(received_time):
    return max(local_time, received_time)


def transfer_money(to_client):
    pass


def save_local_state():
    pass


def record_incoming_msgs():
    '''
    When channel has received marker stop recording
    When all channels has stopped recording send local state and state to the
    machine that initialized the snapshot
    1. Make dict for all incoming channels and array for those who hasn't
    recieved a marker yet.
    2. When processing msg from incoming_queue put in dict if no marker has been
    recieved on that channel
    3. When the array is empty the the local snapshot is complete
    '''
    pass


def send_markers():
    '''Send markers on all outgoing channels'''
    pass


def init_snapshot():
    '''All incoming channels are empty'''
    save_local_state()
    send_markers()


def start_snapshot():
    '''
    1. Save local snapshot
    2. Send MARKERS on all outgoing channels
    3. Listen for MARKERS on incomming channels
    (have own thread for always listening)
    '''
    save_local_state()
    send_markers()
    record_incoming_msgs()


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

        message_str = user_input + ",{},{}EOM".format(local_time, port)  # EOM (end of message) splits messages
        message_binary = bytes(message_str, encoding="ascii")

        elif user_input == "exit":
            try:
                connection.send(bytes("exit", encoding="ascii"))
            finally:
            connection.close()
            break
        else:
            print("unrecognized command, please try read, like, or exit")


def listen_for_messages(connection):
    # TODO: Handle transfers and snapshot
    '''
    Snapshot
    When receiving first MARKER on channel c
    Save local state

    '''
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

            if message_arr[0] == "marker":


            if message_arr[0] == "like":
                request_source_port = message_arr[2]
                print("Machine {} wants the lock".format(request_source_port))
                response_str = "ack {},{},{}EOM".format(request_source_port,local_time, port)
                response_binary = bytes(response_str, encoding="ascii")


t = Thread(target=send_messages, args=(tcpClient, ))
threads.append(t)
t.start()

t = Thread(target=listen_for_messages, args=(tcpClient, ))
threads.append(t)
t.start()

for t in threads:
    t.join()
tcpClient.close()
