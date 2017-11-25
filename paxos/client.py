import socket
from config import cluster
from time import sleep


address_choice = input("Which datacenter do you want to connect to? (A, B or C) ")
data_center_addr = cluster[address_choice]
#data_center_addr = ("localhost", 1337)
connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_msg(data):
    msg = bytes(data, encoding="ascii")
    connection.sendto(msg, data_center_addr)
    print("Message sent to", data_center_addr)


def process_user_input(user_input):
    words = user_input.split(" ")
    command = words[0]
    if len(words) > 1:
        arg = words[1]

    if command == "show":
        send_msg("show")
    elif command == "buy" and arg.isdigit():
        send_msg("{},{}".format(command, arg))
    else:
        print("Couldn't recognize the command", user_input)


while True:
    user_input = input("Send msg to datacenter: ")
    process_user_input(user_input)
