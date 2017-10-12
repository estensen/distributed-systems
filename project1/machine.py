import socket
import sys
from threading import Thread

host = "localhost"
port = int(sys.argv[1])
BUFFER_SIZE = 1024 
threads = []

tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpClient.connect((host, port))


def like_post():
    # TODO: Make sure read and write are atomic
    with open("likes.txt", "r+") as f:
        current_likes = int(f.read())
        print("Current likes:",current_likes)
        new_likes = current_likes + 1
        f.seek(0)
        f.truncate()
        f.write(str(new_likes))
    f.close()


def send_messages(connection):
    while True:
        message = input("Please enter a message to send to all clients: ")
        binary_message = bytes(message, encoding="ascii")
        connection.send(binary_message)
        if message == "exit":
            connection.close()
            break


def listen_for_messages(connection):
    while True:
        binary_data = connection.recv(BUFFER_SIZE)
        data = binary_data.decode("utf-8")
        if not data: #server closed connection
            print("Server closed connection")
            connection.close()
            break
        print("Received data", data)


t = Thread(target=send_messages, args=(tcpClient, ))
threads.append(t)
t.start()

t = Thread(target=listen_for_messages, args=(tcpClient, ))
threads.append(t)
t.start()

for t in threads:
    t.join()
tcpClient.close()
