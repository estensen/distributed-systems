import socket
from time import sleep
from threading import Thread
from config import cluster

BUFFER_SIZE = 1024

identifier = input("Which datacenter do you want to connect to? (A, B or C) ")
server_addr = cluster[identifier]
client_addr = (server_addr[0], server_addr[1] + 10)

server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_sock.bind(client_addr)


def send_msg(data):
    msg = bytes(data, encoding="ascii")
    server_sock.sendto(msg, server_addr)
    print("Message sent to", server_addr)


def process_user_input(user_input):
    words = user_input.split(" ")
    command = words[0]
    if len(words) > 1:
        arg = words[1]

    if command == "show":
        send_msg("show," + str(client_addr[1]))
    elif command == "buy" and arg.isdigit():
        send_msg("{},{},{}".format(command, arg, client_addr[1]))
    else:
        print("Couldn't recognize the command", user_input)


def listen():
    while True:
        data, addr = client_sock.recvfrom(BUFFER_SIZE)
        msg = data.decode("utf-8")
        print(msg)


listen_thread = Thread(target=listen)
listen_thread.start()


while True:
    user_input = input("Send msg to datacenter: ")
    process_user_input(user_input)
