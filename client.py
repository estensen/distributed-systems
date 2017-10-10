# Python TCP Client A
import socket 
import sys

host = "localhost"
port = int(sys.argv[1])
BUFFER_SIZE = 2000 
 
tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpClientA.connect((host, port))

data = tcpClientA.recv(BUFFER_SIZE)
print("Received data", data)
tcpClientA.close()

