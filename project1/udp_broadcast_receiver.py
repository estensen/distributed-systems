import socket
from random import random

port = int(input("Port: "))
server_address = ("localhost", port)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Starting up on {} port {}".format(*server_address))
sock.bind(server_address)

while True:
    print("Waiting to receive msg")
    data, address = sock.recvfrom(32)

    print("Received {} bytes from {}".format(len(data), address))
    print(data.decode("utf-8"))

    if data:
        response = "ack" + str(port)
        if random() > 0.5:
            response = "lock" + str(port)
        binary_response = bytes(response, encoding="ascii")
        sent = sock.sendto(binary_response, address)
        print("Sent '{}' back to {}".format(response, address))
