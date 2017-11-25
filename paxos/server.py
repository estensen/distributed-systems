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
        self.tickets_available = 20

        self.proposal_id = 0
        self.proposal_val = None
        self.next_proposal_num = 1
        self.last_accepted_num = 0
        self.last_accepted_proposer_id = 0
        self.last_accepted_val = None
        self.promised_id = (0, 0)

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
        proposal_num = self.proposal_id[0]
        proposal_id = self.proposal_id[1]
        data = "prepare,{},{}".format(proposal_num, proposal_id)
        self.send_data_to_all(data)

    def recv_prepare(self, msg_list):
        proposal_num, proposer_id = msg_list[1:]
        proposal_id = (int(proposal_num), int(proposer_id))
        if proposal_id >= self.promised_id:
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

        if self.proposal_id < (int(last_accepted_num), int(last_accepted_proposer_id)):
            # An acceptor has already accepted a val
            self.proposal_val = last_accepted_val

        self.recv_promises_uid.add(from_uid)
        if not self.leader:
            if len(self.recv_promises_uid) >= QUORUM_SIZE:
                self.send_accepts()

    def send_accepts(self):
        self.recv_accepted_uid = set()
        data = "accept,{},{},{}".format(self.proposal_id[0], self.proposal_id[1], self.proposal_val)
        self.send_data_to_all(data)

    def recv_accept(self, msg_list):
        proposal_num, proposer_id, proposal_val = msg_list[1:]
        proposal_id = (int(proposal_num), int(proposer_id))

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

    def recv_accepted(self, msg_list):
        proposal_num, proposer_id, from_uid, proposal_val = msg_list[1:]
        self.recv_accepted_uid.add(from_uid)

        if len(self.recv_accepted_uid) >= QUORUM_SIZE:
            if not self.leader:
                self.leader = True
                print("I am leader")
            self.send_learn()

    def send_learn(self):
        proposal_num = self.proposal_id[0]
        proposal_id = self.proposal_id[1]
        data = "learn,{},{},{}".format(proposal_num, proposal_id, self.proposal_val)
        self.send_data_to_all(data)

    def commit_to_log(self, msg_list):
        msg = msg_list[1:]
        self.log.append(msg)
        print("log", self.log)

    def send_data(self, data, addr):
        msg = bytes(data, encoding="ascii")
        self.sock.sendto(msg, addr)
        if data[:9] != "heartbeat":
            print("Message {} sent to {}".format(data, addr))

    def send_data_to_all(self, data):
        if data == "election":
            # Temporary to inject msgs
            self.send_prepare()
        else:
            for identifier, addr in cluster.items():
                self.send_data(data, addr)

    def listen(self):
        print("Listening")
        while True:
            data, addr = self.sock.recvfrom(BUFFER_SIZE)
            msg = data.decode("utf-8")

            msg_list = msg.split(",")
            command = msg_list[0]

            if command != "heartbeat":
                print("Received {} from {}".format(msg, addr))
                print("msg_list", msg_list)

            if command == "buy":
                amount = msg_list[1]
                print("Buy " + amount + " pls!")
                # Send client msg back

                if self.leader:
                    print("Will buy")
                    self.proposal_val = amount
                    self.send_accepts()
                else:
                    print("Have to relay to leader")

            elif command == "show":
                addr = ("localhost", int(msg_list[1]))
                # Send local log to client
                log_str = ",".join(map(str, self.log))
                self.send_data(log_str, addr)

            # Phase 1
            elif command == "prepare":
                self.recv_prepare(msg_list)
            elif command == "promise":
                self.recv_promise(msg_list)

            # Phase 2
            elif command == "accept":
                self.recv_accept(msg_list)
            elif command == "accepted":
                self.recv_accepted(msg_list)

            # Phase 3
            elif command == "learn":
                tickets = msg_list[3]
                print(tickets)
                if tickets.isdigit() and self.tickets_available - int(tickets) > 0:
                    self.tickets_available -= int(tickets)
                    print(str(self.tickets_available) + " left")

                    self.commit_to_log(msg_list)

            elif command == "heartbeat":
                self.last_recv_heartbeat = time()
            else:
                print("Message command {} not recognized".format(command))

    def heartbeat(self):
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
