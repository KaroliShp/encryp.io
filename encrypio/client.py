import socket
import threading
import time
import sys
from threading import Thread
import os
import ssl

from encrypio.messages import receive_json_message, send_json_message, check_connection_client
from encrypio.p2p.p2p_client import P2P_Client
from encrypio.p2p.p2p_server import P2P_Server
from encrypio.security import load_key, key_to_bytes, bytes_to_key


# Dummy TLS client/server certificates and keys
SERVER_SNI_HOSTNAME = 'example.com'
SERVER_CERT = 'ssl/server.crt'
CLIENT_CERT = 'ssl/client.crt'
CLIENT_KEY = 'ssl/client.key'


class SendMessageThread(Thread):

    def __init__(self,c):
        """
        Send messages to provided connection
        :param c: socket object
        """
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.c = c


    def run(self):
        """
        Send messages to provided connection
        """
        while not self._stop_event.is_set():
            uid = input('')
            try:
                send_json_message(self.c, { 'UID' : str(uid) })
            except OSError as e:
                break


    def stop(self):
        """
        Stop the message thread
        """
        self._stop_event.set()


class Client:

    def __init__(self, uid, ik, pk, server_address, server_port):
        """
        Client class
        :param uid: client uid
        :param ik: client public key
        :param pk: client private key
        :param address: IP address of the client
        :param port: Port of the client
        """
        # Client info
        self._uid = uid
        self._ik = ik
        self._pk = pk

        # Server info
        self._server_address = server_address
        self._server_port = server_port

        # Client socket
        self._client_socket = None

    
    def _setup_sockets(self):
        """
        Set up sockets for the client and connect to the server with TLS
        """
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=SERVER_CERT)
        context.load_cert_chain(certfile=CLIENT_CERT, keyfile=CLIENT_KEY)

        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self._client_socket = context.wrap_socket(self._client_socket, server_side=False, server_hostname=SERVER_SNI_HOSTNAME)
        self._client_socket.connect((self._server_address, self._server_port))


    def _verify_with_server(self):
        """
        Send UID and public key to the server to verify
        """
        # Send message to the server
        time.sleep(1)
        send_json_message(self._client_socket, { 'UID' : self._uid, 'IK' : key_to_bytes(self._ik).hex() })

        # Receive response
        response_msg = receive_json_message(self._client_socket)
        check_connection_client(response_msg)
        print(f'Server ({response_msg["Response"]}): {response_msg["Message"]}')
        if response_msg['Response'] == 'Failure':
            print('Quitting...')
            sys.exit(0)

    
    def _send_message(self):
        """
        Create thread for sending messages to server
        :return: send thread object
        """
        send_thread = SendMessageThread(self._client_socket)
        send_thread.daemon = True
        send_thread.start()
        return send_thread
    

    def _listen(self, send_thread):
        """
        Listen for server messages
        """
        peer_msg = None

        while True:
            peer_msg = receive_json_message(self._client_socket)
            check_connection_client(peer_msg)
    
            # Incoming P2P connection
            if peer_msg['Response'] == 'P2P' and 'Message' in peer_msg:
                print(f'\nServer: {peer_msg["Message"]}')
            elif peer_msg['Response'] == 'P2P':
                print(f'\nServer: Initiate P2P with UID: {peer_msg["PeerUID"]}, IP: {peer_msg["PeerIP"]}, IK: {bytes_to_key(bytes.fromhex(peer_msg["PeerIK"]))}')
                send_thread.stop()
                self._client_socket.close()
                print(f'Close connection to the server, so that we can perform P2P')
                break
        
        return peer_msg


    def _start_p2p_server(self, peer_msg):
        """
        Start P2P with peer as a server
        :param peer_msg: peer information
        """
        host = '0.0.0.0'
        port = peer_msg['ServerPort']

        peer_uid = peer_msg['PeerUID']
        peer_ip = peer_msg['PeerIP']
        peer_key = bytes.fromhex(peer_msg['PeerIK'])

        print(f'\nServer in P2P. IP: {host}. Port: {port}. UID: {self._uid}. Peer UID: {peer_uid}. Peer IP: {peer_ip}. Peer IK: {bytes_to_key(peer_key)}')
        p2p_s = P2P_Server(host, port, self._uid, peer_uid, peer_ip, bytes_to_key(peer_key), self._pk)
        p2p_s.start()
    
    
    def _start_p2p_client(self, peer_msg):
        """
        Start P2P with peer as a client
        :param peer_msg: peer information
        """
        time.sleep(2)
        
        peer_host = peer_msg['PeerIP'][0]
        peer_port = peer_msg['PeerPort']

        peer_uid = peer_msg['PeerUID']
        peer_key = bytes.fromhex(peer_msg['PeerIK'])

        print(f'\nClient in P2P. Peer IP: {peer_host}. Peer port: {peer_port}. UID: {self._uid}. Peer UID: {peer_uid}. Peer IK: {bytes_to_key(peer_key)}')
        p2p_c = P2P_Client(peer_host, peer_port, self._uid, peer_uid, bytes_to_key(peer_key), self._pk)
        p2p_c.start()
    
    
    def start(self):
        """
        Start the client
        """
        print(f'Starting the client...')

        self._setup_sockets()
        print(f'Connected to: {self._server_address}:{str(self._server_port)}. TLS established')

        self._verify_with_server()

        send_thread = self._send_message()
        peer_msg = self._listen(send_thread)

        if peer_msg['Server'] == True:
            self._start_p2p_server(peer_msg)
        else:
            self._start_p2p_client(peer_msg)


if __name__ == '__main__':
    # Provide UID from command line
    if len(sys.argv) != 2:
        print('Correct usage: python3 client.py --uid')
        sys.exit(0)
    uid = sys.argv[1]

    # Load corresponding keys
    key_file = f'keys/{uid}_key.pem'
    if os.path.isfile(key_file):
        pk = load_key(key_file)
        ik = pk.public_key()
        print(f'Public key loaded for {uid}: {key_to_bytes(ik).hex()}')

    # Start the client
    client = Client(uid, ik, pk, '0.0.0.0', 5000)
    client.start()
