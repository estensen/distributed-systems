import socket


ip = "localhost"
# port = int(input("Port: "))
port = 555
ports = [5000, 5001]
message = "lock{}".format(port)
binary_message = bytes(message, encoding="ascii")

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
        received_ack_from = []

        for p in ports:
            sock.sendto(binary_message, (ip, p))

            print("Waiting for response")
            binary_data, server = sock.recvfrom(16)
            data = binary_data.decode("utf-8")
            print("Received {!r}".format(data))

            if data[:3] == "ack":
                print("Add")
                received_ack_from.append(p)

            if len(ports) == len(received_ack_from):
                print("Lock on file acquired")
                like_post()

    finally:
        print("Closing socket")
        sock.close()


acquire_lock()
