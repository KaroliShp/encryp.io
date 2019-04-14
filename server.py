from database import Client, db_find, db_update, db_print
from helper import receive_json_message, send_json_message
from security import load_key, key_to_bytes

import socket
import threading
import sys
import json
import time
import ssl

# https://www.electricmonk.nl/log/2018/06/02/ssl-tls-client-certificate-verification-with-python-v3-4-sslcontext/
SERVER_CERT = 'ssl/server.crt'
SERVER_KEY = 'ssl/server.key'
CLIENT_CERTS = 'ssl/client.crt'

ADDR = '0.0.0.0'
PORT = 5000

BUFF_SIZE = 1024

connections = []

# Fake database
database = [Client("Klevas", key_to_bytes(load_key('keys/klevas_key.pem').public_key())), Client("Berzas", key_to_bytes(load_key('keys/berzas_key.pem').public_key()))]

def print_connections():
    """
    Print all connections to the server
    """
    print('\nConnections:')
    for c in connections:
        print(f'{c[1]}:{c[2]}')
    print('\n')

def verify_user(data):
    """
    Check if user exists in the database and if the provided public key is correct according to the database
    """
    res = db_find(database, data['UID'])
    return (not res is None) and (res.IK == bytes.fromhex(data['IK']))

def establish_p2p(c1, ca1, uid1, uid2):
    """
    Establish p2p between the 2 clients
    """
    # Check if UID is not identical
    if uid1 == uid2:
        print(f'Cannot establish P2P with yourself')
        send_json_message(c1, { 'Response' : 'P2P', 'Message' : f'Cannot establish P2P with yourself'})
        return False

    # Check if UID exists
    res = db_find(database, uid2)
    if not res:
        print(f'User with UID {uid2} doesnt exist')
        send_json_message(c1, { 'Response' : 'P2P', 'Message' : f'User {uid2} does not exist'})
        return False

    # Check if UID is online
    for c in connections:
        # UID is online, notify both parties
        if c[2] == uid2:
            print(f'Establising P2P between {uid1}:{ca1} and {uid2}:{c[1]}')
            
            send_json_message(c1, { 'Response' : 'P2P', 'PeerUID' : uid2, 'PeerIP' : c[1], 'PeerIK' : res.IK.hex(), 'Server' : True, 'ServerPort' : 5002})
            send_json_message(c[0], { 'Response' : 'P2P', 'PeerUID' : uid1, 'PeerIP' : ca1, 'PeerPort' : 5002, 'PeerIK' : (db_find(database, uid1).IK).hex(), 'Server' : False })

            return True
    
    print(f'User {uid2} is not currently online')
    send_json_message(c1, { 'Response' : 'P2P', 'Message' : f'User {uid2} is not currently online'})
    return False

def client_handler(c, ca, uid):    
    while True:
        send_json_message(c, { 'Response' : 'Success', 'Message' : 'Send UID with whom youd like to communicate' } )

        # Receive UID with whom to communicate
        uid_msg = receive_json_message(c)
        if uid_msg is None:
            print(f'{uid}:{ca} has disconnected')
            connections.remove((c, ca, uid))
            break
        print(f'\nClient {uid}:{ca} wishes to communicate with {uid_msg["UID"]}')

        # Establish P2P connection
        if establish_p2p(c, ca, uid, uid_msg['UID']):
            break

def client_gateway(c, ca):
    print(f'Client {ca} goes through gateway')

    # Identity confirmation
    verification_msg = receive_json_message(c)
    if verification_msg is None:
        print(f'{ca} has disconected')
        return
    res = verify_user(verification_msg)

    # Give response to the client
    if not res:
        send_json_message(c, { 'Response' : 'Failure', 'Message' : 'Could not authenticate with the server' } )
        print(f'Ending connection with client {ca}')
        c.close()
        print_connections()
        return

    print(f'Client {ca} has successfully authenticated with the server')
    
    # Add to connections
    found = False
    for i, conn in enumerate(connections):
        if conn[2] == verification_msg['UID']:
            connections[i] = (c, ca, verification_msg['UID'])
            found = True
            break
    if not found:
        connections.append((c, ca, verification_msg['UID']))
    print_connections()

    # Handle the client
    client_handler(c, ca, verification_msg['UID'])

def main():
    print(f'\nStarting the server...')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print(f'Socket created successfully...')

    s.bind((ADDR, PORT))
    print(f'Socket binded to {ADDR}:{str(PORT)} successfully...')

    s.listen(2)

    # Run infinite listening loop for clients
    while True:
        client, client_address = s.accept()
        print(f'Client {client_address} has connected to the server')

        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        """
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1
        """
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_cert_chain(certfile=SERVER_CERT, keyfile=SERVER_KEY)
        context.load_verify_locations(cafile=CLIENT_CERTS)
        client = context.wrap_socket(client, server_side=True)
        print(f'TLS established with client {client_address}')

        # Start client handling thread
        client_thread = threading.Thread(target=client_gateway, args=(client, client_address))
        client_thread.daemon = True
        client_thread.start()
    
if __name__ == '__main__':
    main()