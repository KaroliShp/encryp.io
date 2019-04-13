from helper import receive_json_message, send_json_message, check_connection_client
from p2p import P2P_Server, P2P_Client

import socket
import threading
import json
import time
import sys
from threading import Thread

HOST = '192.168.43.102'
PORT = 5000

CLIENT_HOST = '0.0.0.0'

BUFSIZ = 1024

UID = ''
IK = ''

class SendMessageThread(Thread):
    def __init__(self,c):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.c = c

    def run(self):
        while not self._stop_event.is_set():
            uid = input('')
            try:
                send_json_message(self.c, { 'UID' : str(uid) })
            except OSError as e:
                break

    def stop(self):
        self._stop_event.set()

def main():
    # Setup client
    print(f'Starting the client...')

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print(f'Client socket created successfully')

    client_socket.connect((HOST, PORT))
    print(f'Connected to: {HOST}:{str(PORT)}')

    # Verify with the server
    time.sleep(1)
    send_json_message(client_socket, { 'UID' : UID, 'IK' : IK })

    # Receive response
    response_msg = receive_json_message(client_socket)
    check_connection_client(response_msg)
    print(f'Server ({response_msg["Response"]}): {response_msg["Message"]}')
    if response_msg['Response'] == 'Failure':
        print('Quitting...')
        sys.exit(0)
    
    # Create thread for sending messages to server
    send_thread = SendMessageThread(client_socket)
    send_thread.daemon = True
    send_thread.start()

    peer_msg = None
    # Listen for server messages
    while True:
        peer_msg = receive_json_message(client_socket)
        check_connection_client(peer_msg)

        # Incoming P2P connection
        if peer_msg['Response'] == 'P2P' and 'Message' in peer_msg:
            print(f'\nServer: {peer_msg["Message"]}')
        elif peer_msg['Response'] == 'P2P':
            print(f'\nServer: Initiate P2P with UID: {peer_msg["PeerUID"]}, IP: {peer_msg["PeerIP"]}, IK: {peer_msg["PeerIK"]}')
            send_thread.stop()
            client_socket.close()
            print(f'Close connection to the server, so that we can perform P2P')
            break

    # P2P act as a server
    if peer_msg['Server'] == True:
        host = '0.0.0.0'
        port = peer_msg['ServerPort']
        uid = UID

        peer_uid = peer_msg['PeerUID']
        peer_ip = peer_msg['PeerIP']
        peer_key = peer_msg['PeerIK']

        print(f'\nServer in P2P. IP: {host}. Port: {port}. UID: {uid}. Peer UID: {peer_uid}. Peer IP: {peer_ip}. Peer IK: {peer_key}')
        p2p_s = P2P_Server(host, port, uid, peer_uid, peer_ip, peer_key)
        p2p_s.run()
    # P2P act as a client
    else:
        time.sleep(2)
        
        peer_host = peer_msg['PeerIP'][0]
        peer_port = peer_msg['PeerPort']
        uid = UID

        peer_uid = peer_msg['PeerUID']
        peer_key = peer_msg['PeerIK']

        print(f'\nClient in P2P. Peer IP: {peer_host}. Peer port: {peer_port}. UID: {uid}. Peer UID: {peer_uid}. Peer IK: {peer_key}')
        p2p_c = P2P_Client(peer_host, peer_port, uid, peer_uid, peer_key)
        p2p_c.run()

if __name__ == '__main__':
    # Provide UID and IK from command line
    if len(sys.argv) != 3:
        print('Correct usage: python3 client.py --uid --ik')
        sys.exit(0)
    UID = sys.argv[1]
    IK = sys.argv[2]

    main()
