import socket
import threading
import sys

ADDR = '0.0.0.0'
PORT = 5000

BUFF_SIZE = 1024

connections = []

def broadcast(message, c):
    print(f'(Broadcasting) {message}')
    for connection in connections:
        if c != connection:
            connection.send(message.encode())

def client_handler(c, ca):
    while True:
        data = c.recv(BUFF_SIZE).decode()

        broadcast(f'{ca}: {data}', c)
        
        if not data:
            print(f'Connection with {ca} has been lost')
            break

def main():
    print(f'Starting the server...')

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