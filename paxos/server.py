import socket
from threading import Thread
from config import cluster

BUFFER_SIZE = 1024
threads = []

class Server:
    def __init__(self, server_addr):
        self.server_addr = server_addr
        self.log = []
        self.setup()
        self.run()

    def send_data(self, data, addr):
        print(data)
        msg = bytes(data, encoding="ascii")
        if addr != self.server_addr:
            self.sock.sendto(msg, addr)
            print("Message sent to", addr)

    def send_data_to_all(self, data):
        for identifier, addr in cluster.items():
            self.send_data(data, addr)

    def listen(self):
        while True:
            data, addr = self.sock.recvfrom(BUFFER_SIZE)
            msg = data.decode("utf-8")
            self.log.append(msg)
            print(msg)
            if msg == "yo":
                return_msg = "Return"
                self.send_data(return_msg, addr)


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
