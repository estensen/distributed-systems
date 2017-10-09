import socket
from threading import Thread
from time import sleep
from random import randint


ip = "localhost"
port = 555
ports = [5000, 5001]
message = "lock{}".format(port)
binary_message = bytes(message, encoding="ascii")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
received_ack_from = []
unprocessed_requests = []


def like_post():
    with open("likes.txt", "r+") as f:
        current_likes = int(f.read())
        print("Current likes:",current_likes)
        new_likes = current_likes + 1
        f.seek(0)
        f.truncate()
        f.write(str(new_likes))
    f.close()


def acquire_lock(port_index):
    print("Sending {!r}".format(message))

    t = Thread(target=send_msg, args=(port_index, ))
    t.start()


def send_msg(port_index):
    port = ports[port_index]
    print("Send to: ", port)
    sock.sendto(binary_message, (ip, port))

    print("Waiting for response")
    binary_data, server = sock.recvfrom(32)
    data = binary_data.decode("utf-8")

    if data[:3] == "ack":
        # Generalize and check here if data != ack?
        print("Received ack from " + str(port))
        received_ack_from.append(port)
    else:
    #if data[:4] == "lock":
        # Decide priorities
        # Add to queue
        # Won't contain duplicates later
        # TODO: Find a way to wait if an ack is not receive.
        # Don't send a lock request before it's resolved
        unprocessed_requests.append(port)
        print("Received lock from " + str(port))

    if len(ports) == len(received_ack_from):
        print("Lock on file acquired")
        like_post()

    # Try different timing
    sleep(randint(1, 3))


def acquire_locks():
    for like in range(5):
        for port_index in range(2):
            acquire_lock(port_index)
        print("Unprocessed reqs: ", unprocessed_requests)
        sleep(1)
    print("Closing socket")
    sock.close()


acquire_locks()
