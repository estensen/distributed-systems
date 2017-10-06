import socket
import sys

server_address = ("localhost", 5000)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Starting up on {} port {}".format(*server_address))
sock.bind(server_address)

while True:
    print("Waiting to receive msg")
    data, addr = sock.recvfrom(4096)

    print("Received {} bytes from {}".format(len(data), addr))
    print(data.decode("utf-8"))

    if data:
        sent = sock.sendto(data, addr)
        print("Sent {} bytes back to {}".format(sent, addr))