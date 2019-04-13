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
database = [Client("Klevas", "0000", "1111", "2222", "3331", "3332", "3333", "3334", "3335"), Client("Berzas", "0001", "1112", "2223", "3341", "3342", "3343", "3344", "3345")]

def verify_user(data):    
    # Such user doesn't exist in the database or public key is incorrect
    res = db_find(database, data['UID'])
    if res is None or (not res.IK == data['IK']):
        return False

    # Update the database entries with passed parameters
    res.SPK = data['SPK']
    res.SIG = data['SIG']
    res.OPK1 = data['OPK1']
    res.OPK2 = data['OPK2']
    res.OPK3 = data['OPK3']
    res.OPK4 = data['OPK4']
    res.OPK5 = data['OPK5']

    db_update(database, res)

    return True

def broadcast(message, c):
    print(f'(Broadcasting) {message}')
    for connection in connections:
        if c != connection:
            connection.send(message.encode())

def client_handler(c, ca):

    print('X3DH 1')

    # Identity confirmation
    verification_msg = receive_json_message(c)
    res = verify_user(verification_msg)

    # Give response to the client
    if res:
        send_json_message(c, { 'Response' : 'Success', 'Message' : 'Send UID with whom youd like to communicate' } )
    else:
        send_json_message(c, { 'Response' : 'Failure', 'Message' : 'Bad message' } )

    # Receive UID with whom to communicate
    uid_msg = receive_json_message(c)
    print(f'Client wishes to communicate with {uid_msg["UID"]}')
    db_find()

    """
    while True:
        data = c.recv(BUFF_SIZE).decode()

        broadcast(f'{ca}: {data}', c)
        
        if not data:
            print(f'Connection with {ca} has been lost')
            break
    """

def main():
    print(f'\nStarting the server...')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    print(f'Socket created successfully...')

    s.bind((ADDR, PORT))
    print(f'Socket binded to {ADDR}:{str(PORT)} successfully...')

    s.listen(2)

    while True:
        client, client_address = s.accept()
        print(f'Client {client_address} has connected to the server')

        client_thread = threading.Thread(target=client_handler, args=(client, client_address))
        client_thread.daemon = True
        client_thread.start()

        connections.append(client)
    
if __name__ == '__main__':
    main()