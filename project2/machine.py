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

MARKER = "marker"
BUFFER_SIZE = 1024
NUM_MACHINES = 4
threads = []
outgoing_queue = []
incoming_queue = []
mutex = Lock()

tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpClient.connect((host, port))


def transfer_money(to_client):
    pass


def auto_transfer_money():
    '''
    Every 10 sec 0.2 probability of sending a random amountto another client
    Don't send more money than you have
    Add delay in message_server
    '''
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


def message_to_string(msg):
    pass


def user_input_to_message(user_input):
    # EOM (end of message) splits messages so they can be parsed correctly
    message_str = user_input + ",{},{}EOM".format(local_time, port)
    message_binary = bytes(message_str, encoding="ascii")


def send_markers():
    '''Send markers on all outgoing channels'''
    mutex.acquire()
    msg = user_input_to_message(MARKER)
    try:
        connection.send(msg)
    finally:
        mutex.release()


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
    send_markers(connection)
    record_incoming_msgs()


def exit():
    mutex.acquire()
    try:
        connection.send(bytes("exit", encoding="ascii"))
    finally:
        mutex.release()
    connection.close()
    break


def process_outgoing_msgs(connection):
    '''Message format: "<command>,<port>,<local_time>'''
    while True:
        user_input = input("Available commands: snapshot and exit\n")

        if user_input == "snapshot:
            init_snapshot(connection)
        elif user_input == "exit":
            exit(connection)
        else:
            print("Unrecognized command, please try snapshot or exit")


def process_incoming_msgs(connection):
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

            local_time = update_local_time(int(message_arr[1]))
            print("Local time: ", local_time)

            if message_arr[0] == "marker":


            if message_arr[0] == "like":
                request_source_port = message_arr[2]
                print("Machine {} wants the lock".format(request_source_port))
                response_str = "ack {},{},{}EOM".format(request_source_port,local_time, port)
                response_binary = bytes(response_str, encoding="ascii")


t1 = Thread(target=process_incoming_msgs, args=(tcpClient, ))
threads.append(t1)

t2 = Thread(target=process_outgoing_msgs, args=(tcpClient, ))
threads.append(t2)


for t in threads:
    t.join()
tcpClient.close()
