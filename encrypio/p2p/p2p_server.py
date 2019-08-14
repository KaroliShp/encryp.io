import socket
import threading
import os

from encrypio.messages import send_json_message, receive_json_message
from encrypio.security import generate_symmetric_key, encrypt_message, decrypt_message


class P2P_Server:

    def __init__(self, host, port, uid, peer_uid, peer_ip, peer_ik, private_key):
        """
        Server in P2P connection
        :param host: host IP address
        :param port: host port
        :param peer_uid: UID of the peer connection
        :param peer_ip: peer IP address
        :param peer_ik: peer public key
        :param private_key: host private key
        """
        # Open server socket
        self.p2p_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.p2p_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.p2p_s.bind((host, port))
        self.p2p_s.listen(2)

        # Set incoming peer connection information
        self.peer_uid = peer_uid
        self.peer_ip = peer_ip
        self.peer_ik = peer_ik

        # Set server info
        self.uid = uid
        self.private_key = private_key
    
    
    def _send_message(self):
        """
        Send encrypted message to the connected client
        """
        while True:
            msg = input('')
            aes_key = generate_symmetric_key(self.private_key, self.peer_ik)
            iv = os.urandom(16)
            encrypted_msg = encrypt_message(aes_key, iv, msg.encode())
            send_json_message(self.p2p_c, { 'Message' : encrypted_msg.hex(), 'iv' : iv.hex() })


    def start(self):
        """
        Run P2P server, listen for connections and communicate with the client
        """
        # Wait for expected connection
        while True:
            p2p_c, p2p_ca = self.p2p_s.accept()

            if not p2p_ca[0] == self.peer_ip[0]:
                print(f'Unknown connection from {p2p_ca}, close')
                p2p_c.close()
                continue

            self.p2p_c = p2p_c 
            self.p2p_ca = p2p_ca
            break
        
        print(f'Established P2P connection with {self.p2p_ca}')
        print(f'\nPress enter to join P2P chat with {self.peer_uid}')

        # Start thread for message sending
        send_thread = threading.Thread(target=self._send_message)
        send_thread.daemon = True
        send_thread.start()

        # Listen for incoming messages from the client
        while True:
            msg = receive_json_message(self.p2p_c)

            if msg is None:
                print(f'Lost connection to the peer {self.peer_uid}:({self.peer_ip}), closing...')
                break

            aes_key = generate_symmetric_key(self.private_key, self.peer_ik)
            decrypted_msg = decrypt_message(aes_key, bytes.fromhex(msg['iv']), bytes.fromhex(msg['Message']))
            print(f'{self.peer_uid} ({self.p2p_ca}): {decrypted_msg.decode()}')