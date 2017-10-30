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
mutex = Lock()

outgoing_queue = []
incoming_queue = []
ongoing_snapshots = {}

tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpClient.connect((host, port))


def transfer_money(amount, to_client):
    print("Transfered {} to {}".format(amount, to_client))


def auto_transfer_money():
    '''
    Every 10 sec 0.2 probability of sending a random amountto another client
    Don't send more money than you have
    Add delay in message_server
    '''
    pass


def save_local_state():
    '''Dict with initiators id as key?'''
    print("Local state saved")


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


def receive_msg(connection):
    message_binary = connection.recv(BUFFER_SIZE)
    message_str = message_binary.decode("utf-8")
    print(message_str)
    return message_str


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
        print("MARKERS sent on all outgoing channels")
    finally:
        mutex.release()


def init_snapshot():
    '''All incoming channels are empty'''
    print("Initating snapshot")
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
    '''
    Old msg format: "<command>,<port>,<local_time>
    New msg format: "<command>,<src_id>,<dst_id>,opt=<initiator_id>"
    id = port
    initiator_id if marker msg
    '''
    while True:
        user_input = input("Available commands: snapshot and exit\n")

        if user_input == "snapshot:
            init_snapshot(connection)
        elif user_input == "exit":
            exit(connection)
        else:
            print("Unrecognized command, please try snapshot or exit")


def process_msg(msg):
    msg_arr = msg.split(",")

    command = msg_arr[0]

    if command == "exit":
        print("Exiting...")
        connection.close()
        break

    elif command == "marker":
        src_id = msg_arr[2]
        initiator_id = msg_arr[3]
        if ongoing_snapshots[initiator_id]:
            if ongoing_snapshots[initiator_id][src_id]:
                record_msg_to_channel_state(initiator_id, src_id, msg)
            else:
                # Done, send local snapshot and channels to initiator
        else:
            # First marker to this machine
            start_snapshot(initiator_id)


def process_incoming_msgs(connection):
    # TODO: Handle transfers and snapshot
    # TODO: Handle recieve snapshots from other nodes when done
    '''
    Snapshot
    When receiving first MARKER on channel c
    Save local state
    '''
    while True:
        msg = recieve_msg(connection)

        if not msg:
            connection.close()
            print("Closing connection...")
            break

        msg_list = msg.split("EOM")  # Because msgs can arrive in chunks

        for i in range(len(msg_list)-1):
            process_msg(msg_list[i])


t1 = Thread(target=process_incoming_msgs, args=(tcpClient, ))
threads.append(t1)

t2 = Thread(target=process_outgoing_msgs, args=(tcpClient, ))
threads.append(t2)


for t in threads:
    t.join()
tcpClient.close()
