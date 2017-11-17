import socket
from threading import Thread
from math import ceil
from config import cluster

BUFFER_SIZE = 1024
threads = []
quorum_size = ceil(len(cluster) / 2)  # (n / 2) + 1

class Server:
    def __init__(self, server_addr):
        self.uid = server_addr
        self.leader = False
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
        while True:
            data, addr = self.sock.recvfrom(BUFFER_SIZE)
            msg = data.decode("utf-8")
            self.log.append(msg)
            print("Received {} from {}".format(msg, addr))
            if msg == "prepare":
                promise_msg = "promise"
                self.send_data(promise_msg, addr)
                print("Returned promise")
            if msg == "promise":
                accept_msg = "accept"
                self.send_data(accept_msg, addr)
            if msg == "accept":
                accepted_msg = "accepted"
                self.send_data(accepted_msg, addr)
            if msg == "accepted":
                self.recv_promises.add(addr)
                if len(self.recv_promises) >= quorum_size:
                    self.leader = True
                    print("I am leader")


    def setup(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.server_addr)
        print("Server socket created")
        print("Server addr:", self.server_addr)

        listen_thread = Thread(target=self.listen)
        threads.append(listen_thread)
        listen_thread.start()
        print("Listening")

    def run(self):
        pass
        #send_thread = Thread(target=send_data, args=(self.sock, ))
        #threads.append(send_thread)
        #send_thread.start()
