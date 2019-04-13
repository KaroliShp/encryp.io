from helper import receive_json_message, send_json_message
from cryptography import generate_signature, verify_signature, calculate_shared_key

from socket import AF_INET, socket, SOCK_STREAM
import threading
import json
import time
import sys

HOST = '192.168.1.188'
PORT = 5000

BUFSIZ = 1024

UID = ''
IK = ''

def verify():
    return { 
        'UID' : UID, 
        'IK' : IK
    }

def create_peer_uid(uid):
    return {
        'UID' : uid
    }

def send_message(c):
    while True:
        uid_msg = create_peer_uid(input('You: '))
        send_json_message(c, uid_msg)

def main():
    # Setup client
    print(f'Starting the client...')

    client_socket = socket(AF_INET, SOCK_STREAM)
    print(f'Client socket created successfully')

    client_socket.connect((HOST, PORT))
    print(f'Connected to: {HOST}:{str(PORT)}')

    # Verify with the server
    time.sleep(1)
    send_json_message(client_socket, verify())

    # Receive response
    response_msg = receive_json_message(client_socket)
    print(f'Server ({response_msg["Response"]}): {response_msg["Message"]}')
    if response_msg['Response'] == 'Failure':
        print('Quitting...')
        sys.exit(0)

    # Create thread for sending messages
    send_thread = threading.Thread(target=send_message, args=(client_socket,))
    send_thread.daemon = True
    send_thread.start()

    while True:
        peer_msg = receive_json_message(client_socket)
        
        # Incoming P2P connection
        if peer_msg["Response"] == 'P2P':
            if 'Message' in peer_msg:
                print(f'\nServer interrupted: {peer_msg["Message"]}')
            else:
                print(f'\nServer interrupted: Initiate P2P with UID: {peer_msg["PeerUID"]}, IP: {peer_msg["PeerIP"]}, IK: {peer_msg["PeerIK"]}')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Correct usage: python3 client.py --uid --ik')
        sys.exit(0)
    UID = sys.argv[1]
    IK = sys.argv[2]

    main()
