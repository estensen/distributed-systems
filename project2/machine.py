import socket
import sys
from threading import Thread
from multiprocessing import Lock
from random import choice, randint
from time import sleep

local_account_balance = 1000
host = "localhost"
port = int(sys.argv[1])
process_id = port

MARKER = "marker"
BUFFER_SIZE = 1024
NUM_MACHINES = 2
threads = []
mutex = Lock()
other_clients = [12345, 12346]
other_clients.remove(port)

final_snapshot = {}
ongoing_snapshots = {}
channel_states = {}

tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpClient.connect((host, port))


def transfer_money(amount, to_client):
    print("Transfered {} to {}".format(amount, to_client))


def auto_transfer_money():
    '''
    Every 10 sec 0.2 probability of sending a random amount to another client
    Don't send more money than you have
    Add delay in message_server
    '''
    sleep(randint(10, 14))
    random_amount = randint(1, 20)
    random_client = choice(other_clients)
    if local_account_balance > random_amount:
        transfer_money(random_amount, random_client)


def save_local_state():
    '''Dict with initiators id as key?'''
    print("Local state saved")


def record_incoming_msgs(initiator_id):
    '''
    When channel has received marker stop recording
    When all channels has stopped recording send local state and state to the
    machine that initialized the snapshot
    1. Make dict for all incoming channels and list for those who hasn't
    received a marker yet.
    2. When processing msg from incoming_queue put in dict if no marker has been
    received on that channel
    3. When the list is empty the the local snapshot is complete
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


def user_input_to_message(user_input, initiator_id):
    # EOM (end of message) splits messages so they can be parsed correctly
    # New msg format: "<command>,<src_id>,opt=<dst_id>,opt=<initiator_id>"
    message_str = user_input + ",{},{}EOM".format(port, initiator_id)
    message_binary = bytes(message_str, encoding="ascii")
    return message_binary


def send_markers(connection, initiator_id):
    '''Send markers on all outgoing channels'''
    mutex.acquire()
    msg = user_input_to_message(MARKER, initiator_id)
    try:
        connection.send(msg)
        print("MARKERS sent on all outgoing channels")
    finally:
        mutex.release()


def init_snapshot(connection):
    '''All incoming channels are empty'''
    print("Initating snapshot")
    initiator_id = port
    save_local_state()
    final_snapshot = {}
    send_markers(connection, initiator_id)



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


def print_final_snapshot():
    print("Snapshot complete...")
    for client, state in final_snapshot:
        print(client)
        print(state)


def exit():
    mutex.acquire()
    try:
        connection.send(bytes("exit", encoding="ascii"))
    finally:
        mutex.release()
    connection.close()


def process_user_input(connection):
    '''
    Old msg format: "<command>,<port>,<local_time>
    New msg format: "<command>,<src_id>,opt=<dst_id>,opt=<initiator_id>"
    '''
    while True:
        user_input = input("Available commands: snapshot and exit\n")

        if user_input == "snapshot":
            init_snapshot(connection)
        # send_money
        elif user_input == "exit":
            exit(connection)
        else:
            print("Unrecognized command, please try snapshot or exit")


def process_msg(msg):
    msg_list = msg.split(",")
    command = msg_list[0]
    src_id = msg_list[1]

    if command == "exit":
        print("Exiting...")
        connection.close()

    elif command == "marker":
        initiator_id = msg_list[3]
        if ongoing_snapshots[initiator_id]:
            if ongoing_snapshots[initiator_id][src_id]:
                record_msg_to_channel_state(initiator_id, src_id, msg)
            else:
                # Done, send local snapshot and channels to initiator
                pass
        else:
            # First marker to this machine
            start_snapshot(initiator_id)

    elif command == "snapshot":
        snapshot = msg_list[3:]
        final_snapshot[src_id] = snapshot
        print("Snapshot reveived from {}".format(src_id))
        if len(final_snapshot) == len(other_clients):
            print_final_snapshot()

    else:
        print("Unknown command!")


def process_incoming_msgs(connection):
    # TODO: Handle transfers and snapshot
    # TODO: Handle receive snapshots from other nodes when done
    '''
    Snapshot
    When receiving first MARKER on channel c
    Save local state
    '''
    while True:
        msg = receive_msg(connection)

        if not msg:
            connection.close()
            print("Closing connection...")
            break

        msg_list = msg.split("EOM")  # Because msgs can arrive in chunks

        for i in range(len(msg_list)-1):
            process_msg(msg_list[i])


t1 = Thread(target=process_incoming_msgs, args=(tcpClient, ))
threads.append(t1)
t1.start()

t2 = Thread(target=process_user_input, args=(tcpClient, ))
threads.append(t2)
t2.start()

t3 = Thread(target=auto_transfer_money)
threads.append(t3)
t3.start()


for t in threads:
    t.join()
tcpClient.close()
