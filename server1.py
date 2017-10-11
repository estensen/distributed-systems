import socket 
from threading import Thread 
import sys #command line args

###########################################################
#
# @Author: Albert Chen, Havard Anda Estensen
# 
# @Description: opens a server with NUM_CLIENTS
# when it receives a message from a client, send
# it to all other clients
# 
# @README:
# Currently written in python 2, can switch to python 3
#
# To run the program: python server1.py <port>
# Create as many client threads as required by NUM_CLIENT
# python client.py <port1>
# python client.py <port2>
# ...
#
# Start sending messages on client threads, other clients
# will receive the messages
# exit on the client thread will exit the client
#
###########################################################

connections = []
threads = [] #threads that create the initial socket connections
listen_threads = [] #threads to listen to client threads, 1 thread for each client
if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 12345 #default port if user doesn't enter one
NUM_CLIENTS=3 #change to however many clients you want

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

def listen_for_messages(connection):
    print("Listening on connection", connection)
    while True:
        data = connection.recv(BUFFER_SIZE)
        if (not data or data == "exit"): #if data is empty, it means client closed connection
            print ("Client closed connection")
            connection.close()
            #remove client from the connection list
            connections.remove(connection)
            print("Updated connection list:", connections)
            break

        print("Received data", data, "from connection", connection)
        #send the data to all the other clients
        for other_connection in connections:
            if other_connection != connection:
                other_connection.send(data)

for i in range(NUM_CLIENTS): #establish connections to all clients first
    t = Thread(target=create_connection, args=(port+i, ))
    threads.append(t)
    t.start()

for t in threads: #clean up threads
    t.join()

for i in range(NUM_CLIENTS): #establish a listen thread for all clients
    t = Thread(target=listen_for_messages, args=(connections[i], ))
    listen_threads.append(t)
    t.start()

for t in threads: #clean up threads
    t.join()

