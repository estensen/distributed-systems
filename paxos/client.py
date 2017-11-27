import socket
from time import sleep
from threading import Thread
from config import cluster

BUFFER_SIZE = 1024

class Client:
    def __init__(self):
        self.socket_setup()
        self.thread_setup()

    def socket_setup(self):
        self.identifier = input("Which datacenter do you want to connect to? (A, B or C) ")
        self.server_addr = cluster[self.identifier]
        self.client_addr = (self.server_addr[0], self.server_addr[1] + 10)

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_sock.bind(self.client_addr)

    def send_msg(self, data):
        msg = bytes(data, encoding="ascii")
        self.server_sock.sendto(msg, self.server_addr)
        print("Message sent to", self.server_addr)

    def process_user_input(self, user_input):
        words = user_input.split(" ")
        command = words[0]
        if len(words) > 1:
            arg = words[1]

        if command == "show":
            self.send_msg("show," + str(self.client_addr[1]))
        elif command == "buy" and arg.isdigit():
            self.send_msg("{},{},{}".format(command, arg, self.client_addr[1]))
        elif command == "change":
            self.server_sock.close()
            self.client_sock.close()
            self.socket_setup()
        else:
            print("Couldn't recognize the command", user_input)

    def listen(self):
        while True:
            data, addr = self.client_sock.recvfrom(BUFFER_SIZE)
            msg = data.decode("utf-8")
            print(msg)

    def user_input(self):
        while True:
            user_input = input("Send msg to datacenter: ")
            self.process_user_input(user_input)

    def thread_setup(self):
        listen_thread = Thread(target=self.listen)
        listen_thread.start()

        input_thread = Thread(target=self.user_input)
        input_thread.start()

def run():
    client = Client()

if __name__ == "__main__":
    run()
