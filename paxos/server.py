import socket
from threading import Thread
from random import random
from math import ceil
from time import sleep, time
from config import cluster

BUFFER_SIZE = 1024
threads = []
QUORUM_SIZE = ceil(len(cluster) / 2)  # (n / 2) + 1
HEARTBEAT_FREQ = 3
heartbeat_delta = HEARTBEAT_FREQ * 3 + random() * 8

class Server:
    def __init__(self, server_addr):
        self.uid = server_addr[1]
        self.leader = False
        self.last_recv_heartbeat = None
        self.server_addr = server_addr

        self.proposal_id = None
        self.proposal_val = None
        self.next_proposal_num = 1
        self.last_accepted_num = None
        self.last_accepted_proposer_id = None
        self.last_accepted_val = None
        self.promised_id = None

        self.log = []
        self.setup()
        self.run()

    def set_proposal(self, val):
        if self.proposal_val == None:
            self.proposal_val = val

    def send_prepare(self):
        self.proposal_id = (self.next_proposal_num, self.uid)
        self.next_proposal_num += 1
        self.recv_promises_uid = set()
        self.recv_accepts_uid = set()
        data = "prepare,{},{}".format(self.proposal_id[0], self.proposal_id[1])
        self.send_data_to_all(data)

    def recv_prepare(self, msg_list):
        proposal_num, proposer_id = msg_list[1:]
        proposal_id = (proposal_num, proposer_id)
        if self.promised_id == None or proposal_id >= self.promised_id:
            # Higher than current promise
            self.promised_id = proposal_id

            promise_msg = "promise,{},{},{},{},{},{}".format(
                proposal_num,
                proposer_id,
                self.uid,
                self.last_accepted_num,
                self.last_accepted_proposer_id,
                self.last_accepted_val
            )

            from_addr = ("localhost", int(proposal_id[1]))
            self.send_data(promise_msg, from_addr)
            print("Returned promise")

    def recv_promise(self, msg_list):
        proposal_num, proposer_id, from_uid, last_accepted_num, \
        last_accepted_proposer_id, last_accepted_val = msg_list[1:]

        if last_accepted_num != "None" and last_accepted_proposer_id != "None":
            if self.proposal_id < (int(last_accepted_num), int(last_accepted_proposer_id)):
                # And > id
                # An acceptor has already accepted a val
                self.proposal_val = last_accepted_val

        self.recv_promises_uid.add(from_uid)
        if len(self.recv_promises_uid) >= QUORUM_SIZE:
            self.send_accepts()

    def send_accepts(self):
        data = "accept,{},{},{}".format(self.proposal_id[0], self.proposal_id[1], self.proposal_val)
        self.send_data_to_all(data)

    def recv_accept(self, msg_list):
        proposal_num, proposer_id, proposal_val = msg_list[1:]
        proposal_id = (proposal_num, proposer_id)

        if proposal_id >= self.promised_id:
            # Accept proposal
            self.last_accepted_num = proposal_num
            self.last_accepted_proposer_id = proposer_id
            self.last_accepted_val = proposal_val

            self.send_accept()

    def send_accept(self):
        accepted_data = "accepted,{},{},{},{}".format(self.last_accepted_num, \
            self.last_accepted_proposer_id, self.uid, self.last_accepted_val)
        to_addr = ("localhost", int(self.last_accepted_proposer_id))
        self.send_data(accepted_data, to_addr)

    def recv_accepts(self, msg_list):
        proposal_num, proposer_id, from_uid, proposal_val = msg_list[1:]
        self.recv_accepts_uid.add(from_uid)

        if len(self.recv_accepts_uid) >= QUORUM_SIZE:
            self.leader = True
            print("I am leader")

    def send_data(self, data, addr):
        msg = bytes(data, encoding="ascii")
        if addr != self.server_addr:
            self.sock.sendto(msg, addr)
            print("Message {} sent to {}".format(data, addr))

    def send_data_to_all(self, data):
        if data == "election":
            self.send_prepare()
        else:
            for identifier, addr in cluster.items():
                self.send_data(data, addr)

    def listen(self):
        print("Listening")
        while True:
            data, addr = self.sock.recvfrom(BUFFER_SIZE)
            msg = data.decode("utf-8")
            self.log.append(msg)
            print("Received {} from {}".format(msg, addr))

            msg_list = msg.split(",")
            print("msg_list", msg_list)
            command = msg_list[0]

            if command == "prepare":
                self.recv_prepare(msg_list)
            elif command == "promise":
                self.recv_promise(msg_list)
            elif command == "accept":
                self.recv_accept(msg_list)
            elif command == "accepted":
                self.recv_accepts(msg_list)
            elif command == "heartbeat":
                self.last_recv_heartbeat = time()

    def heartbeat(self):
        print("Heart up and running")
        while True:
            if self.leader:
                self.last_recv_heartbeat = time()
                self.send_data_to_all("heartbeat")
            sleep(HEARTBEAT_FREQ)

    def listen_for_heartbeats(self):
        while True:
            sleep(heartbeat_delta)
            if not self.leader:
                if self.last_recv_heartbeat == None:
                    self.send_data_to_all("election")
                    self.last_recv_heartbeat = time()
                delta = time() - self.last_recv_heartbeat
                if delta > heartbeat_delta:
                    self.send_data_to_all("election")

    def setup(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.server_addr)
        print("Server socket created")
        print("Server addr:", self.server_addr)

        listen_thread = Thread(target=self.listen)
        threads.append(listen_thread)
        listen_thread.start()

        heartbeat_thread = Thread(target=self.heartbeat)
        threads.append(heartbeat_thread)
        heartbeat_thread.start()

        listen_heartbeats_thread = Thread(target=self.listen_for_heartbeats)
        threads.append(listen_heartbeats_thread)
        listen_heartbeats_thread.start()

    def run(self):
        pass
        #send_thread = Thread(target=send_data, args=(self.sock, ))
        #threads.append(send_thread)
        #send_thread.start()
