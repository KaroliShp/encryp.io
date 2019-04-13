import socket
import json

HEADER_BUFF_SIZE = 32

def send_json_message(socket, data):
    message = json.dumps(data)
    header = format(len(message), '032b')
    socket.send(header.encode())
    socket.send(message.encode())

def receive_json_message(socket):
    header = int(socket.recv(HEADER_BUFF_SIZE).decode(), 2)
    message = json.loads(socket.recv(header).decode())
    return message