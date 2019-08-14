import socket
import threading
import os

from encrypio.messages import send_json_message, receive_json_message
from encrypio.security import generate_symmetric_key, encrypt_message, decrypt_message


class P2P_Client:

    def __init__(self, peer_ip, peer_port, uid, peer_uid, peer_ik, private_key):
        """
        Client in P2P connection
        :param peer_ip: IP address of the server
        :param peer_port: port of the server
        :param uid: UID of the client
        :param peer_uid: UID of the peer who starts the server
        :param peer_ik: peer public key
        :param private_key: client private key
        """
        # Open client socket
        self.p2p_c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.p2p_c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Set expected server peer information
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.peer_uid = peer_uid
        self.peer_ik = peer_ik

        # Set client private key
        self.private_key = private_key
    

    def _send_message(self):
        """
        Send encrypted message to the server
        """
        while True:
            msg = input('')
            aes_key = generate_symmetric_key(self.private_key, self.peer_ik)
            iv = os.urandom(16)
            encrypted_msg = encrypt_message(aes_key, iv, msg.encode())
            send_json_message(self.p2p_c, { 'Message' : encrypted_msg.hex(), 'iv' : iv.hex() })

            
    def start(self):
        """
        Run the P2P client, connect to the server and send messages
        """
        # Connect to the server
        self.p2p_c.connect((self.peer_ip, self.peer_port))        
        print(f'Established P2P connection with ({self.peer_ip},{self.peer_port})')
        print(f'\nPress enter to join P2P chat with {self.peer_uid}')

        # Start thread for message sending
        send_thread = threading.Thread(target=self._send_message)
        send_thread.daemon = True
        send_thread.start()

        # Listen for incoming messages from the server
        while True:
            msg = receive_json_message(self.p2p_c)

            if msg is None:
                print(f'Lost connection to the peer {self.peer_uid}:({self.peer_ip},{self.peer_port}), closing...')
                break

            aes_key = generate_symmetric_key(self.private_key, self.peer_ik)
            decrypted_msg = decrypt_message(aes_key, bytes.fromhex(msg['iv']), bytes.fromhex(msg['Message']))
            print(f'{self.peer_uid} ({self.peer_ip},{self.peer_port}): {decrypted_msg.decode()}')