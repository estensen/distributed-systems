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
