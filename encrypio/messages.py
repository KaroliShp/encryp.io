import socket
import json
import sys


# Default header buffer size
HEADER_BUFF_SIZE = 32  # bytes


def send_json_message(socket, data):
    """
    Send message to a provided socket in JSON
    :param socket: socket object
    :param data: message to be sent (dictionary)
    """
    message = json.dumps(data)
    header = format(len(message), '032b')
    socket.send(header.encode())
    socket.send(message.encode())


def receive_json_message(socket):
    """
    Receive JSON message from the provided socket
    :param socket: socket object
    :return: received message (dictionary)
    """
    raw_msg = socket.recv(HEADER_BUFF_SIZE).decode()
    if not raw_msg:
        return None
    header = int(raw_msg, 2)
    message = json.loads(socket.recv(header).decode())
    return message


def check_connection_client(msg):
    """
    Check connection to the server from the client
    :param msg: message from the server 
    """
    if msg is None:
        print(f'Server has disconnected. Quitting...')
        sys.exit(0)