import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 53001)
print('starting up')
sock.bind(server_address)

while True:
    print('waiting to receive message')
    data, address = sock.recvfrom(4096)
    
    # print('received {} bytes from {}'.format(len(data), address))
    print(data.decode('utf8'))
    
