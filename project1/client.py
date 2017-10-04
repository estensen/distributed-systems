import socket


class Client:
    def __init__(self, node_number):
        """Init data for testing a single client"""
        self.node_number = node_number
        self.post = "The cake is a lie!!"
        self.numOfLikes = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def increment_like(self):
        """Add one like to the post"""
        self.numOfLikes += 1
        print(self.post)
        print("Likes: ", self.numOfLikes)


if __name__ == '__main__':
    # Init the client
    client = Client(1)
    print("Node {} initialized".format(client.node_number))

    client.socket.connect(("localhost", 10000))

    try:
        msg = b"Like!"
        client.socket.sendall(msg)

    finally:
        client.socket.close()
