import socket
from config import cluster
from time import sleep


#address_choice = input("Which datacenter do you want to connect to? (A, B or C) ")
#data_center_addr = cluster[address_choice]
data_center_addr = ("localhost", 1337)
connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.connect(data_center_addr)


while True:
    user_input = input("Send msg to datacenter: ")
    msg = bytes(user_input, encoding="ascii")
    if not msg:
        connection.close()
        print("Closing connection...")
    connection.send(msg)
    print("Message sent to", data_center_addr)
