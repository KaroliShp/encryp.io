import socket
import threading
import json
import ssl

from database.client_model import ClientModel
from database.database import Database
from messages import receive_json_message, send_json_message
from security import load_key, key_to_bytes


# Dummy TLS client/server certificates and keys
SERVER_CERT = 'ssl/server.crt'
SERVER_KEY = 'ssl/server.key'
CLIENT_CERTS = 'ssl/client.crt'

# Dummy client keys
KLEVAS_KEY_PATH = 'keys/klevas_key.pem'
BERZAS_KEY_PATH = 'keys/berzas_key.pem'


class Server:

    def __init__(self, address, port, database):
        """
        Server for clients to connect
        :param address: IP address of the server
        :param port: port of the server
        """
        # Server info
        self._address = address
        self._port = port

        # Server connections
        self._connections = []

        # Server database
        self._database = database

        # Server socket
        self._server_socket = None

    
    def _print_connections(self):
        """
        Print all connections to the server
        """
        print('\nConnections:')
        for c in self._connections:
            print(f'{c[1]}:{c[2]}')
        print('\n')

    
    def _verify_user(self, data):
        """
        Check if user exists in the database and if the provided public key is correct according to the database
        :param data: verification message returned by the client
        :return: True if user is verified, false otherwise
        """
        res = self._database.find_client_by_uid(data['UID'])
        return (res is not None) and (res.get_ik() == bytes.fromhex(data['IK']))


    def _establish_p2p(self, c1, ca1, uid1, uid2):
        """
        Establish P2P connection between the clients
        :param c1: initiator client socket object
        :param c2: receiver client socket object
        :param uid1: UID of the initiator
        :param uid2: UID of the receiver
        :return: True if connection has been established, false otherwise
        """
        # Check if UID is not identical
        if uid1 == uid2:
            print(f'Cannot establish P2P with yourself')
            send_json_message(c1, { 'Response' : 'P2P', 'Message' : f'Cannot establish P2P with yourself'})
            return False

        # Check if UID exists
        res = self._database.find_client_by_uid(uid2)
        if res is None:
            print(f'User with UID {uid2} doesnt exist')
            send_json_message(c1, { 'Response' : 'P2P', 'Message' : f'User {uid2} does not exist'})
            return False

        # Check if UID is online
        for c in self._connections:
            # UID is online, notify both parties
            if c[2] == uid2:
                print(f'Establising P2P between {uid1}:{ca1} and {uid2}:{c[1]}')
                
                send_json_message(c1, { 'Response' : 'P2P', 'PeerUID' : uid2, 'PeerIP' : c[1], 'PeerIK' : res.get_ik().hex(), 'Server' : True, 'ServerPort' : 5002})
                send_json_message(c[0], { 'Response' : 'P2P', 'PeerUID' : uid1, 'PeerIP' : ca1, 'PeerPort' : 5002, 'PeerIK' : self._database.find_client_by_uid(uid1).get_ik().hex(), 'Server' : False })
                return True
        
        print(f'User {uid2} is not online at the moment, please try later')
        send_json_message(c1, { 'Response' : 'P2P', 'Message' : f'User {uid2} is not online at the moment, please try later'})
        return False


    def _client_handler(self, c, ca, uid):    
        """
        Handle authenticated client for connections with other clients
        :param c: client socket object
        :param ca: client IP address
        """
        while True:
            send_json_message(c, { 'Response' : 'Success', 'Message' : 'Send UID with whom youd like to communicate' } )

            # Receive UID with whom to communicate
            uid_msg = receive_json_message(c)
            if uid_msg is None:
                print(f'{uid}:{ca} has disconnected')
                self._connections.remove((c, ca, uid))
                break
            print(f'\nClient {uid}:{ca} wishes to communicate with {uid_msg["UID"]}')

            # Establish P2P connection
            if self._establish_p2p(c, ca, uid, uid_msg['UID']):
                break


    def _client_gateway(self, c, ca):
        """
        Gateway for a new client connection
        :param c: client socket object
        :param ca: client IP address
        """
        print(f'Client {ca} goes through gateway')

        # Identity confirmation
        verification_msg = receive_json_message(c)
        if verification_msg is None:
            print(f'{ca} has disconected')
            return
        res = self._verify_user(verification_msg)

        # Give response to the client
        if not res:
            send_json_message(c, { 'Response' : 'Failure', 'Message' : 'Could not authenticate with the server' } )
            print(f'Ending connection with client {ca}')
            c.close()
            self._print_connections()
            return

        print(f'Client {ca} has successfully authenticated with the server')
        
        # Add to connections list
        found = False
        for i, conn in enumerate(self._connections):
            if conn[2] == verification_msg['UID']:
                self._connections[i] = (c, ca, verification_msg['UID'])
                found = True
                break
        if not found:
            self._connections.append((c, ca, verification_msg['UID']))
        self._print_connections()

        # Handle the client
        self._client_handler(c, ca, verification_msg['UID'])

    
    def _setup_sockets(self):
        """
        Set up sockets for the server
        """
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self._address, self._port))
        self._server_socket.listen(2)

    
    def _establish_tls(self, client):
        """
        Establish TLS connection with the client
        :param client: client socket object
        :return: new client socket object
        """
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_cert_chain(certfile=SERVER_CERT, keyfile=SERVER_KEY)
        context.load_verify_locations(cafile=CLIENT_CERTS)
        client = context.wrap_socket(client, server_side=True)
        return client

    
    def _listen(self):
        """
        Run infinite listening loop for client connection
        """
        while True:
            client, client_address = self._server_socket.accept()
            print(f'Client {client_address} has connected to the server')

            client = self._establish_tls(client)
            print(f'TLS established with client {client_address}')

            # Start client handling thread
            client_thread = threading.Thread(target=self._client_gateway, args=(client, client_address))
            client_thread.daemon = True
            client_thread.start()
    
    
    def start(self):
        """
        Start the server
        """
        print(f'\nStarting the server...')

        self._setup_sockets()
        print(f'Server socket binded to {self._address}:{str(self._port)} successfully. Listening to incoming connections')
        
        self._listen()
        print('Stopping the server...')


if __name__ == '__main__':
    # Fake database
    clients_list = [ ClientModel("klevas", key_to_bytes(load_key(KLEVAS_KEY_PATH).public_key())), ClientModel("berzas", key_to_bytes(load_key(BERZAS_KEY_PATH).public_key()))]
    database = Database(clients_list)

    # Start the server
    server = Server('0.0.0.0', 5000, database)
    server.start()