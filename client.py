from helper import receive_json_message, send_json_message

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
    message = receive_json_message(client_socket)
    print(f'Server ({message["Response"]}): {message["Message"]}')
    if message['Response'] == 'Failure':
        print('Quitting...')
        sys.exit(0)

    uid_msg = create_peer_uid(input('You: '))
    send_json_message(client_socket, uid_msg)

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
