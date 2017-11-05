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
user_id = process_id

MARKER = "marker"
BUFFER_SIZE = 1024
NUM_MACHINES = 4
threads = []
mutex = Lock()

ongoing_snapshots = []
# Need to initialize other_clients process ids
other_clients = []
''' Dictionary with initiator_id as key '''
channel_states = {}

tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpClient.connect((host, port))


def transfer_money(amount, to_client):
    ''' Initiator id = 0 when only a transfer
        msg format: <command>,<src_id>,<dst_id>,<initiator_id> '''
    #Alternate msg format: msg = [amount, user_id, to_client, 0]
    msg = [amount, user_id, to_client]
    self.local_account_balance -= amount
    msg_str = ", ".join(map(str,msg))
    send_message(msg_str)
    print("Transfered {} to {}".format(amount, to_client))


def auto_transfer_money():
    '''
    Every 10 sec 0.2 probability of sending a random amountto another client
    Don't send more money than you have
    Add delay in message_server
    '''
    pass


def save_local_state(init_id):
    '''Dict with initiators id as key'''
    channel_states[init_id] = local_account_balance
    print("Local state saved")


def record_incoming_msgs(initiator_id):
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
    # list comprehension to add list with all ids as keys except itself and initiator_id
    ongoing_snapshots[initiator_id] = []
    # list comprehension to add dict for all incoming channels
    channel_states[initiator_id] = {}


def receive_msg(connection):
    message_binary = connection.recv(BUFFER_SIZE)
    message_str = message_binary.decode("utf-8")
    print(message_str)
    return message_str


###### Change format:
def user_input_to_message(user_input):
    # EOM (end of message) splits messages so they can be parsed correctly
    message_str = user_input + ",{},{}EOM".format(local_time, port)
    message_binary = bytes(message_str, encoding="ascii")
    return message_binary


def send_message(message):
    '''Send msg to message_server that is not a marker'''
    mutex.acquire()
    msg = user_input_to_message(message)
    try:
        connection.send(msg)
        #print("MARKERS sent on all outgoing channels")
    finally:
        mutex.release()


def send_markers(init_id):
    '''Send markers on all outgoing channels'''
    mutex.acquire()
    #msg_marker = [MARKER, user_id, 0, init_id]
    msg_marker = [MARKER, user_id, init_id]
    msg_marker_str = ", ".join(map(str,msg_marker))
    msg = user_input_to_message(msg_marker_str)
    try:
        connection.send(msg)
        print("MARKERS sent on all outgoing channels")
    finally:
        mutex.release()


def init_snapshot():
    '''All incoming channels are empty'''
    print("Initating snapshot")
    save_local_state(user_id)
    send_markers(user_id)
    start_snapshot(user_id)


def start_snapshot(init_id):
    '''
    1. Save local snapshot
    2. Send MARKERS on all outgoing channels
    3. Listen for MARKERS on incomming channels
    (have own thread for always listening)
    '''
    ongoing_snapshots.append(init_id)
    if init_id == user_id:
        #record_incoming_msgs() - Check process_msg
    else:    
        save_local_state()
        send_markers(init_id)
        #record_incoming_msgs() - Check process_msg


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
    New msg format: "<command>,<src_id>,opt=<dst_id>,opt=<initiator_id>"
    '''
    while True:
        user_input = input("Available commands: snapshot and exit\n")
        if user_input == "snapshot:
            init_snapshot(connection)
        # send_money
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
        src_id = msg_arr[1]
        initiator_id = msg_arr[3]
        ''' If second marker'''
        if initiator_id in ongoing_snapshots:
            ongoing_snapshots.remove(initiator_id)
            # Send state to initiator
            ''' snapshot = list of local_accout_balance + messages recorded'''
            ''' snapshot msg format = "snapshot", src_id, recv_id, snapshot'''
            snap = []
            snapshot = channel_states[initiator_id]
            snap = ["snapshot", user_id, initiator_id, snapshot]
            snapshot_str = ", ".join(map(str,snap))
            send_message(snapshot_str)
        else:
            start_snapshot(initiator_id)

    ''' If message being sent is a transaction
        msg format = <amount><src_id><dest_id> '''
    elif isinstance(command, int):
        if command in ongoing_snapshots:
            ''' Entering message into local state recording '''
            state[initiator_id].append(msg)
        else:
            amount = int(command)
            local_account_balance+=amount


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
