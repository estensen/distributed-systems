import socket
from threading import Thread
from time import sleep


ip = "localhost"
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
    print("Sending {!r}".format(message))
    received_ack_from = []

    for p in ports:  # Not async yet
        sock.sendto(binary_message, (ip, p))

        print("Waiting for response")
        binary_data, server = sock.recvfrom(16)
        data = binary_data.decode("utf-8")

        if data[:3] == "ack":
            print("Received ack from " + str(p))
            received_ack_from.append(p)

        if len(ports) == len(received_ack_from):
            print("Lock on file acquired")
            like_post()

    sleep(3)


def acquire_locks():
    for i in range(5):
        acquire_lock()
    print("Closing socket")
    sock.close()


def listening():
    while True:
        print("...listening...")
        sleep(2)


threads = []
t1 = Thread(target=acquire_locks)
t1.start()
t2 = Thread(target=listening)
t2.start()
