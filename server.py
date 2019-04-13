from database import Client, db_find, db_update, db_print
from helper import receive_json_message, send_json_message

import socket
import threading
import sys
import json

ADDR = '0.0.0.0'
PORT = 5000

BUFF_SIZE = 1024

connections = []

# Fake database
database = [Client("Klevas", "0000"), Client("Berzas", "0001")]

def print_connections():
    print('\nConnections:')
    for c in connections:
        print(f'{c[1]}:{c[2]}')
    print('\n')

def verify_user(data):
    """
    Check if user exists in the database and if the provided public key is correct
    """
    res = db_find(database, data['UID'])
    return (not res is None) and (res.IK == data['IK'])

def establish_p2p(c1, ca1, uid1, uid2):
    """
    Establish p2p between the 2 clients
    """
    if uid1 == uid2:
        send_json_message(c1, { 'Response' : 'P2P', 'Message' : f'Cannot establish P2P with yourself'})
        return False

    print(f'Trying to establish p2p between {uid1}:{ca1} and {uid2}')

    # Check if UID exists
    res = db_find(database, uid2)
    if not res:
        print(f'User with UID {uid2} doesnt exist')
        send_json_message(c1, { 'Response' : 'P2P', 'Message' : f'User {uid2} does not exist'})
        return False
    print(f'User {uid2} exists in the database, checking for connection')

    # Check if UID is online
    for c in connections:
        # UID is online, notify both parties
        if c[2] == uid2:
            print(f'Establising P2P between {uid1}:{ca1} and {uid2}:{c[1]}')
            send_json_message(c1, { 'Response' : 'P2P', 'PeerUID' : uid2, 'PeerIP' : c[1], 'PeerIK' : res.IK })
            send_json_message(c[0], { 'Response' : 'P2P', 'PeerUID' : uid1, 'PeerIP' : ca1, 'PeerIK' : db_find(database, uid1).IK })
            return True
    
    print(f'User {uid2} is not currently online')
    send_json_message(c1, { 'Response' : 'P2P', 'Message' : f'User {uid2} is not online'})
    return False

def client_handler(c, ca, uid):
    print(f'Client {ca} has successfully authenticated with the server')
    
    while True:
        send_json_message(c, { 'Response' : 'Success', 'Message' : 'Send UID with whom youd like to communicate' } )

        # Receive UID with whom to communicate
        uid_msg = receive_json_message(c)
        if uid_msg is None:
            print(f'Disconnecting client {uid}:{ca}')
            connections.remove((c, ca, uid))
            break
        print(f'\nClient {uid}:{ca} wishes to communicate with {uid_msg["UID"]}')

        # Establish P2P connection
        establish_p2p(c, ca, uid, uid_msg['UID'])

def client_gateway(c, ca):
    print(f'Client {ca} goes through gateway')

    # Identity confirmation
    verification_msg = receive_json_message(c)
    res = verify_user(verification_msg)

    # Give response to the client
    if not res:
        send_json_message(c, { 'Response' : 'Failure', 'Message' : 'Could not authenticate with the server' } )
        print(f'Ending connection with client {ca}')
        c.close()
        print_connections()
        return

    # Add to connections
    connections.append((c, ca, verification_msg['UID']))
    print_connections()

    # Handle the client
    client_handler(c, ca, verification_msg['UID'])

def main():
    print(f'\nStarting the server...')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    print(f'Socket created successfully...')

    s.bind((ADDR, PORT))
    print(f'Socket binded to {ADDR}:{str(PORT)} successfully...')

    s.listen(2)

    # Run infinite listening loop for clients
    while True:
        client, client_address = s.accept()
        print(f'Client {client_address} has connected to the server')

        # Start client handling thread
        client_thread = threading.Thread(target=client_gateway, args=(client, client_address))
        client_thread.daemon = True
        client_thread.start()
    
if __name__ == '__main__':
    main()