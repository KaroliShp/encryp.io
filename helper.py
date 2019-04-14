import socket
import json
import sys 

HEADER_BUFF_SIZE = 32

def send_json_message(socket, data):
    message = json.dumps(data)
    header = format(len(message), '032b')
    socket.send(header.encode())
    socket.send(message.encode())

def receive_json_message(socket):
    raw_msg = socket.recv(HEADER_BUFF_SIZE).decode()
    if not raw_msg:
        return None
    header = int(raw_msg, 2)
    message = json.loads(socket.recv(header).decode())
    return message

def check_connection_client(msg):
    if msg is None:
        print(f'Server has disconnected. Quitting...')
        sys.exit(0)