import socket

server_address = ("localhost", 5000)
MSG = b"Hello, world!"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    print("Sending {!r}".format(MSG))
    sent = sock.sendto(MSG, server_address)

    print("Waiting for response")
    data, server = sock.recvfrom(4096)
    print("Received {!r}".format(data.decode("utf-8")))
finally:
    print("Closing socket")
    sock.close()