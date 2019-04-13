from helper import receive_json_message, send_json_message
from cryptography import generate_signature, verify_signature, calculate_shared_key

from socket import AF_INET, socket, SOCK_STREAM
import threading
import json

HOST = '192.168.43.102'
PORT = 5000

BUFSIZ = 1024

def verify():
    return { 
        'UID' : 'Klevas', 
        'IK' : '0000',
        'SPK' : '1110',
        'SIG' : '2220',
        'OPK1' : '3330',
        'OPK2' : '3331',
        'OPK3' : '3332',
        'OPK4' : '3333',
        'OPK5' : '3334'
    }

def create_peer_uid(uid):
    return {
        'UID' : uid
    }

def send_message(client_socket):
    while True:
        message = input('You: \n')
        client_socket.send(message.encode())

def main():
    print(f'Starting the client...')

    client_socket = socket(AF_INET, SOCK_STREAM)
    print(f'Client socket created successfully')

    client_socket.connect((HOST, PORT))
    print(f'Connected to: {HOST}:{str(PORT)}')

    # Publish keys
    keys_msg = verify()
    send_json_message(client_socket, keys_msg)

    # Receive response
    response_msg = receive_json_message(client_socket)
    print(f'Server ({response_msg["Response"]}): {response_msg["Message"]}')
    if response_msg['Response'] == 'Failure':
        print('Quitting...')
        sys.exit(0)

    # Ask for prekey bundle
    uid_msg = create_peer_uid(input('You: '))
    send_json_message(client_socket, uid_msg)
    bundle_msg = receive_json_message(client)
    if bundle_msg['Response'] == 'Failure':
        print('Failed to retrieve key bundle')
        sys.exit(0)
    key_bundle = bundle_msg['PKBundle']

    # Verify bundle
    res = verify_signature(key_bundle['IK'], key_bundle['SPK'], key_bundle['SIG'])
    if not res:
        print('Signature is wrong')
        sys.exit(0)
    
    # 



    """
    send_thread = threading.Thread(target=send_message, args=(client_socket,))
    send_thread.daemon = True
    send_thread.start()

    while True:
        data = client_socket.recv(BUFSIZ).decode()

        if not data:
            break

        print(f'Received: {data}\nYou:')
    """

if __name__ == '__main__':
    main()
