import socket
import struct

multicast_group = "224.3.29.71"
server_address = ("", 10000)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Starting up on {} port {}".format(*server_address))
sock.bind(server_address)

group = socket.inet_aton(multicast_group)
mreq = struct.pack("4sL", group, socket.INADDR_ANY)
sock.setsockopt(
    socket.IPPROTO_IP,
    socket.IP_ADD_MEMBERSHIP,
    mreq)

while True:
    print("Waiting to receive msg")
    data, address = sock.recvfrom(1024)

    print("Received {} bytes from {}".format(len(data), address))
    print(data.decode("utf-8"))

    if data:
        sent = sock.sendto(b"ack", address)
        print("Sent ack to ", address)