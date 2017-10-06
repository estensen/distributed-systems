import socket
import struct


multicast_group = ("224.3.29.71", 10000)
ID = 1
message = "{} wants the lock".format(ID)
binary_message = bytes(message, encoding="ascii")
print(binary_message)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.2)
time_to_live = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP,
                socket.IP_MULTICAST_TTL,
                time_to_live)

try:
    print("Sending {!r}".format(message))
    sent = sock.sendto(binary_message, multicast_group)

    # Wait for responses from all recipients
    while True:
        print("Waiting for response")
        try:
            data, server = sock.recvfrom(16)
        except socket.timeout:
            print("Timed out, no more responses")
            break
        else:
            print("Received {!r} from {}"
                  .format(data.decode("utf-8"), server))
finally:
    print("Closing socket")
    sock.close()
