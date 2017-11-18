import socket
from threading import Thread
from random import random
from math import ceil
from time import sleep, time
from config import cluster

BUFFER_SIZE = 1024
threads = []
QUORUM_SIZE = ceil(len(cluster) / 2)  # (n / 2) + 1
HEARTBEAT_FREQ = 5
heartbeat_delta = HEARTBEAT_FREQ * 2 + random() * 4

class Server:
    def __init__(self, server_addr):
        self.uid = server_addr
        self.leader = False
        self.last_recv_heartbeat = None
        self.server_addr = server_addr
        self.log = []
        self.setup()
        self.run()

    def prepare(self):
        self.recv_promises = set()

    def send_data(self, data, addr):
        msg = bytes(data, encoding="ascii")
        if addr != self.server_addr:
            self.sock.sendto(msg, addr)
            print("Message {} sent to {}".format(data, addr))

    def send_data_to_all(self, data):
        if data == "election":
            self.prepare()
            data = "prepare"
        for identifier, addr in cluster.items():
            self.send_data(data, addr)

    def listen(self):
        print("Listening")
        while True:
            data, addr = self.sock.recvfrom(BUFFER_SIZE)
            msg = data.decode("utf-8")
            self.log.append(msg)
            print("Received {} from {}".format(msg, addr))
            if msg == "prepare":
                promise_msg = "promise"
                self.send_data(promise_msg, addr)
                print("Returned promise")
            elif msg == "promise":
                accept_msg = "accept"
                self.send_data(accept_msg, addr)
            elif msg == "accept":
                accepted_msg = "accepted"
                self.send_data(accepted_msg, addr)
            elif msg == "accepted":
                self.recv_promises.add(addr)
                if len(self.recv_promises) >= QUORUM_SIZE:
                    self.leader = True
                    print("I am leader")
            elif msg == "heartbeat":
                self.last_recv_heartbeat = time()

    def heartbeat(self):
        print("Heart up and running")
        while True:
            if self.leader:
                self.send_data_to_all("heartbeat")
            sleep(HEARTBEAT_FREQ)

    def listen_for_heartbeats(self):
        while True:
            sleep(HEARTBEAT_FREQ * 2 + random() * 4)
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
