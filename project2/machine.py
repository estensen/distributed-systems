import socket
import sys
from threading import Thread
from multiprocessing import Lock
from random import choice, randint, random
from time import sleep

local_account_balance = 1000
host = "localhost"
port = int(sys.argv[1])
process_id = port

MARKER = "marker"
BUFFER_SIZE = 1024
NUM_MACHINES = 3
threads = []
mutex = Lock()
other_clients = [12345, 12346, 12347]
names = ["Thor", "Odin", "Loke"]
name = names[other_clients.index(port)]
print("{}, ${}".format(name, local_account_balance))
other_clients.remove(port)

final_snapshot = {}
local_snapshot = {}
local_state = {}
ongoing_snapshots = {}
channel_states = {}

tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_client.connect((host, port))


def transfer_money(connection, amount, to_client):
    global local_account_balance
    if amount < local_account_balance:
        local_account_balance -= amount

        msg_str = "{},{},{}EOM".format(amount, port, to_client)
        msg_binary = bytes(msg_str, encoding="ascii")

        mutex.acquire()
        try:
            connection.send(msg_binary)
            print("Transfered {} to {}".format(amount, to_client))
            print("Current balance:", local_account_balance)
        finally:
            mutex.release()
    else:
        print("Not enough $")


def auto_transfer_money(connection):
    '''
    Every 10 sec 0.2 probability of sending a random amount to another client
    Don't send more money than you have
    Add delay in message_server
    '''
    while True:
        sleep(10)
        if (random() < 0.12):
            random_amount = randint(1, 20)
            random_client = choice(other_clients)
            transfer_money(connection, random_amount, random_client)


def save_local_state(initiator_id):
    '''Dict with initiators id as key?'''
    print("Local state saved")
    print(local_snapshot)
    local_state[initiator_id] = local_account_balance


def record_incoming_msgs(initiator_id):
    '''
    Make data struct for new snapshot with initiator_id

    When channel has received marker stop recording
    When all channels has stopped recording send local state and state to the
    machine that initialized the snapshot
    1. Make dict for all incoming channels and list for those who hasn't
    received a marker yet.
    2. When processing msg from incoming_queue put in dict if no marker has been
    received on that channel
    3. When the list is empty the the local snapshot is complete
    '''
    # Save incoming msgs on all channels
    clients = [client for client in other_clients]
    if port != initiator_id:
        clients.remove(initiator_id)  # Already received marker from the initiator

    client_queues = {client: [] for client in clients}
    channel_states[initiator_id] = client_queues

    ongoing_snapshots[initiator_id] = clients

    #print("clients", clients)
    #print("client_queue", client_queues)
    #print("channel_states", channel_states)


def record_msg_to_channel_state(initiator_id, src_id, msg):
    channel_states[initiator_id][src_id] = msg


def receive_msg(connection):
    message_binary = connection.recv(BUFFER_SIZE)
    message_str = message_binary.decode("utf-8")
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
    sleep(randint(3, 5))
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
    local_snapshot[initiator_id] = {}
    save_local_state(initiator_id)
    final_snapshot = {}
    send_markers(connection, initiator_id)
    record_incoming_msgs(initiator_id)


def start_snapshot(connection, initiator_id):
    '''
    1. Save local snapshot
    2. Send MARKERS on all outgoing channels
    3. Listen for MARKERS on incomming channels
    (have own thread for always listening)
    '''
    save_local_state(initiator_id)
    print("local_snapshot", local_snapshot)
    local_snapshot[initiator_id] = {}
    print("local_snapshot", local_snapshot)
    send_markers(connection, initiator_id)
    record_incoming_msgs(initiator_id)


def send_snapshot(connection, initiator_id):
    mutex.acquire()
    msg = "local_snapshot,{},{},{},{}EOM".format(port, initiator_id, local_state[initiator_id], local_snapshot[initiator_id])
    print("local_snapshot", msg)
    binary_msg = bytes(msg, encoding="ascii")
    try:
        connection.send(binary_msg)
        print("Local snapshot sent to", initiator_id)
        del local_snapshot[initiator_id]
        del channel_states[initiator_id]
        del ongoing_snapshots[initiator_id]
    finally:
        mutex.release()


def print_final_snapshot():
    print("####################")
    print("Snapshot complete...")
    print("Own incoming channels:", local_snapshot[port])
    print("Others' incoming channels:", final_snapshot)
    print("####################")


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
        user_input = input("Available commands: snapshot and exit\n$ ")

        if user_input[0].isdigit():
            user_input_list = user_input.split(" ")
            amount = int(user_input_list[0])
            dst_id = user_input_list[1]
            transfer_money(connection, amount, dst_id)

        elif user_input == "snapshot":
            init_snapshot(connection)
        # send_money
        elif user_input == "exit":
            exit(connection)
        else:
            print("Unrecognized command, please try snapshot or exit")


def process_msg(connection, msg):
    global local_account_balance
    print("Incoming msg", msg)

    msg_list = msg.split(",")
    command = msg_list[0]
    src_id = int(msg_list[1])

    if command.isdigit():
        command = int(command)

    if isinstance(command, int):
        print("Receiving ${} from {}".format(command, src_id))
        local_account_balance += command

        if len(ongoing_snapshots) > 0:
            for initiator_id in ongoing_snapshots:
                record_msg_to_channel_state(initiator_id, src_id, msg)

    elif command == "exit":
        print("Exiting...")
        connection.close()

    elif command == "marker":
        print("Receiving marker from", src_id)
        initiator_id = int(msg_list[2])

        if initiator_id in ongoing_snapshots:
            # Already received first marker
            # Channel state is complete => local_snapshot
            local_snapshot[initiator_id][src_id] = channel_states[initiator_id][src_id]
            del channel_states[initiator_id][src_id]
            if len(channel_states[initiator_id]) == 0 and initiator_id != port:
                send_snapshot(connection, initiator_id)

        else:
            # First marker to this machine
            start_snapshot(connection, initiator_id)

    elif command == "local_snapshot":
        snapshot = msg_list[3:]
        final_snapshot[src_id] = snapshot
        print("Snapshot received from {}".format(src_id))
        if len(final_snapshot) == len(other_clients):
            print_final_snapshot()

    else:
        print("Unknown command!")


def process_incoming_msgs(connection):
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
            process_msg(connection, msg_list[i])


t1 = Thread(target=process_incoming_msgs, args=(tcp_client, ))
threads.append(t1)
t1.start()

t2 = Thread(target=process_user_input, args=(tcp_client, ))
threads.append(t2)
t2.start()

t3 = Thread(target=auto_transfer_money, args=(tcp_client, ))
threads.append(t3)
t3.start()


for t in threads:
    t.join()
tcpClient.close()
