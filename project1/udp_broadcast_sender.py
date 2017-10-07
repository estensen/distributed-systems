import socket


ip = "localhost"
port = int(input("Port: "))
ports = [5000, 5001]
message = "Want lock,{}".format(port)
binary_message = bytes(message, encoding="ascii")
print(binary_message)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def like_post():
    with open("likes.txt", "r+") as f:
        current_likes = int(f.read())
        print("Current likes:",current_likes)
        new_likes = current_likes + 1
        f.seek(0)
        f.truncate()
        f.write(str(new_likes))
    f.close()


def acquire_lock():
    try:
        print("Sending {!r}".format(message))
        received_from = []

        for p in ports:
            sock.sendto(binary_message, (ip, p))
            received_from.append(p)

        print("Waiting for response")
        data, server = sock.recvfrom(16)
        print("Received {!r}".format(data.decode("utf-8")))

        print("Received from:", received_from)
        if len(ports) == len(received_from):
            print("Lock on file acquired")
            like_post()

    finally:
        print("Closing socket")
        sock.close()


acquire_lock()
