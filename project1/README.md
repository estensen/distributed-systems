## Using
Specify number of machines in the system at `NUM_MACHINES` in `message_server.py`
```
$ python3 message_server.py
```
For as many ports as specified run
```
$ python3 machine.py <port1>
$ python3 machine.py <port2>
```   
Start sending messages from a machine and the message_server will distribute them to all the machines that are connected.
Exit the machine by sending the message "exit"

#Implementation
Implementing Lamport totally ordered clocks with Ricart-Agrawala Optimization
The read command does not request mutual exclusion of resource. If another process is busy writing, it will loop until it finds an available opening to read.
The like command will call the request resource command to all processes. Other processes will ack if they don't want the resource, and compare if they do want the resource.
The process with the lower local time will receive the resource. If tied, with the lower process id (port) will receive the resource. 


for testing purposes: the like command adds a 5 second delay in order to create collisions whenever necessary

