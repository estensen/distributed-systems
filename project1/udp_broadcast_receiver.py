import socket


port = int(input("Port: "))
server_address = ("localhost", port)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Starting up on {} port {}".format(*server_address))
sock.bind(server_address)

while True:
    print("Waiting to receive msg")
    data, address = sock.recvfrom(16)

    print("Received {} bytes from {}".format(len(data), address))
    print(data.decode("utf-8"))

    if data:
        response = "ack" + str(port)
        binary_response = bytes(response, encoding="ascii")
        sent = sock.sendto(binary_response, address)
        print("Sent ack back to {}".format(sent, address))
