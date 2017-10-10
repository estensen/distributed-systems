import socket 
from threading import Thread 
from SocketServer import ThreadingMixIn 
import sys

connections = []
threads = []
port = 8000

#TCP_PORT = int(sys.argv[1])
BUFFER_SIZE = 1024

def create_connection(port):
    print("connection thread created with port", port)
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcp_server_socket.bind(("localhost", port))
        tcp_server_socket.listen(1)
        print("tcpserver calling accept on port ", port);
        conn, addr = tcp_server_socket.accept()
        print("appending to connections the following info: ", connections, addr)
        connections.append(conn)
    except:
        print("tcp server socket closed")
        tcp_server_socket.close()
        

for i in range(4): #establish connections to all clients first
    t = Thread(target=create_connection, args=(port+i, ))
    threads.append(t)
    t.start()

while True:
    message = raw_input("Please enter a message to send to all clients");
    #if message == "exit": TODO
    print("list of connections", connections)
    for connection in connections:
        connection.send(message)

for t in threads: #clean up threads
    t.join() 
