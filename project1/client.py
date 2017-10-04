class Client:
    def __init__(self):
        """Init data for testing a single client"""
        self.post = "The cake is a lie!!"
        self.numOfLikes = 0

    def increment_like(self):
        """Add one like to the post"""
        self.numOfLikes += 1
        print(self.post)
        print("Likes: {}".format(self.numOfLikes))


if __name__ == '__main__':
    client = Client()
    client.increment_like()
