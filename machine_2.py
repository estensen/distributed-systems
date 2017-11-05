import socket
import thread
from threading import Thread, Lock
import sys
import time
import DSConfig

local_account_balance = 1000

MARKER = "marker"
BUFFER_SIZE = 1024
NUM_MACHINES = 4

threads = []
listen_threads =[]
mutex = Lock()
serv =[]
ongoing_snapshots = []

def IsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class User:
    def __init__(self, user_id):
        ''' Initialize user_id for each client '''
        self.user_id = user_id
        self.other_clients = []
        self.local_account_balance = 1000
        ''' Create list of all other clients '''
        for i in range(0, NUM_MACHINES):
            if i!= user_id:
                self.other_clients.append(i)
            else:
                continue
        ''' Create list for state of the client to be stored '''
        self.state = []

def transfer_money(amount, to_client):
    ''' Initiator id = 0 when only a transfer
        msg format: <command>,<src_id>,<dst_id>,<initiator_id> '''
    #msg = [amount, user_id, to_client, 0]
    msg = [amount, user_id, to_client]
    self.local_account_balance -= amount
    msg_str = ",".join(map(str,msg))
    send_message(msg_str)
        
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
    self.state.append(local_account_balance)
    print("Local state saved")


def receive_msg(connection):
    message_binary = connection.recv(BUFFER_SIZE)
    message_str = message_binary.decode("utf-8")
    print(message_str)
    return message_str

######## Check: 
def user_input_to_message(user_input):
    # EOM (end of message) splits messages so they can be parsed correctly
    message_str = user_input + ",{},{}EOM".format(local_time, port)
    message_binary = bytes(message_str, encoding="ascii")


def send_message(message):
    '''Send msg to message_server'''
    mutex.acquire()
    msg = user_input_to_message(message)
    try:
        connection.send(msg)
        print("MARKERS sent on all outgoing channels")
    finally:
        mutex.release()


def send_markers_not_init(init_id):
    ''' When initiator is not self
        Send markers on all outgoing channels'''
    mutex.acquire()
    #msg_marker = [MARKER, user_id, 0, init_id]
    # Have to convert to array?
    msg_marker = [MARKER, user_id, init_id]
    msg = user_input_to_message(msg_marker)
    try:
        connection.send(msg)
        print("MARKERS sent on all outgoing channels")
    finally:
        mutex.release()


''' send_message, send_markers_not_init
is a replica of send_markers'''
def send_markers():
    '''Send markers on all outgoing channels'''
    mutex.acquire()
    msg_marker = [MARKER,user_id,0] 
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
    send_markers_not_init(user_id)
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
        record_incoming_msgs()
    else:
        #send_markers(connection)
        save_local_state()
        send_markers_not_init(init_id)
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
    New msg format: "<command>,<src_id>,<dst_id>,<initiator_id>"
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

## process_msg1 is original with dictionary
def process_msg1(msg):
    msg_arr = msg.split(",")

    command = msg_arr[0]

    if command == "exit":
        print("Exiting...")
        connection.close()
        break

    elif command == "marker":
        src_id = msg_arr[1]
        initiator_id = msg_arr[3]
        if ongoing_snapshots[initiator_id]:
            if ongoing_snapshots[initiator_id][src_id]:
                record_msg_to_channel_state(initiator_id, src_id, msg)
            else:
                # Done, send local snapshot and channels to initiator
        else:
            # First marker to this machine
            start_snapshot(initiator_id)

    elif IsInt(command):
        if command in ongoing_snapshots:
            # Enter message into list for local state
        else:
            local_account_balance+=amount


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
        ''' If it is the second marker '''
        if initiator_id in ongoing_snapshots:
            ongoing_snapshots.remove(initiator_id)
            # Send state to initiator
            
        ''' First marker recv'd - Recording to begin '''
        else:
            start_snapshot(initiator_id)

    ''' If message being sent is a transaction
        msg format = <amount><src_id><dest_id> '''
    elif IsInt(command):
        if command in ongoing_snapshots:
            ''' Entering message into local state recording '''
            self.state.append(msg)
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



    
        
    
