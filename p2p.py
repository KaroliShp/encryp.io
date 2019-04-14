from helper import send_json_message, receive_json_message
from security import generate_symmetric_key, encrypt_message, decrypt_message, generate_key

import socket
import threading
import time
import os

class P2P_Server:
    def __init__(self, host, port, uid, peer_uid, peer_ip, peer_ik, private_key):
        self.p2p_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.p2p_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.p2p_s.bind((host, port))
        self.p2p_s.listen(2)

        self.peer_uid = peer_uid
        self.peer_ip = peer_ip
        self.peer_ik = peer_ik

        self.private_key = private_key
    
    def send_message(self):
        while True:
            msg = input('')
            aes_key = generate_symmetric_key(self.private_key, self.peer_ik)
            iv = os.urandom(16)
            encrypted_msg = encrypt_message(aes_key, iv, msg.encode())
            send_json_message(self.p2p_c, { 'Message' : encrypted_msg.hex(), 'iv' : iv.hex() })

    def run(self):
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

        send_thread = threading.Thread(target=self.send_message)
        send_thread.daemon = True
        send_thread.start()

        while True:
            msg = receive_json_message(self.p2p_c)
            if msg is None:
                print(f'Lost connection to the peer {self.peer_uid}:({self.peer_ip}), closing...')
                break
            aes_key = generate_symmetric_key(self.private_key, self.peer_ik)
            decrypted_msg = decrypt_message(aes_key, bytes.fromhex(msg['iv']), bytes.fromhex(msg['Message']))
            print(f'{self.peer_uid} ({self.p2p_ca}): {decrypted_msg.decode()}')

class P2P_Client:
    def __init__(self, peer_ip, peer_port, uid, peer_uid, peer_ik, private_key):
        self.p2p_c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.p2p_c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.peer_uid = peer_uid
        self.peer_ik = peer_ik

        self.private_key = private_key
    
    def send_message(self):
        while True:
            msg = input('')
            aes_key = generate_symmetric_key(self.private_key, self.peer_ik)
            iv = os.urandom(16)
            encrypted_msg = encrypt_message(aes_key, iv, msg.encode())
            send_json_message(self.p2p_c, { 'Message' : encrypted_msg.hex(), 'iv' : iv.hex() })

    def run(self):
        self.p2p_c.connect((self.peer_ip, self.peer_port))

        # Key exchange todo
        
        print(f'Established P2P connection with ({self.peer_ip},{self.peer_port})')
        print(f'\nPress enter to join P2P chat with {self.peer_uid}')

        send_thread = threading.Thread(target=self.send_message)
        send_thread.daemon = True
        send_thread.start()

        while True:
            msg = receive_json_message(self.p2p_c)
            if msg is None:
                print(f'Lost connection to the peer {self.peer_uid}:({self.peer_ip},{self.peer_port}), closing...')
                break
            aes_key = generate_symmetric_key(self.private_key, self.peer_ik)
            decrypted_msg = decrypt_message(aes_key, bytes.fromhex(msg['iv']), bytes.fromhex(msg['Message']))
            print(f'{self.peer_uid} ({self.peer_ip},{self.peer_port}): {decrypted_msg.decode()}')