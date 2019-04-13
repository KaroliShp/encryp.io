import socket
import threading
import sys

<<<<<<< HEAD
#Defines Server Values
listensocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Port = 5000
maxConnections = 999
IP = socket.gethostname() #Gets Hostname Of Current Macheine


def main():
    host = ''
    Port = 5000

    listensocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listensocket.bind(('',Port))
    except Exception as e:
        print("Binding error:" + str(e))

    #Opens Server
    listensocket.listen(maxConnections)
    print("Server started at " + IP + " on port " + str(Port))

    #Accepts Incomming Connection
    (clientsocket, address) = listensocket.accept()
    print("New connection made!" + str(address) + "joins the call")


    while True:
        message = clientsocket.recv(1024).decode()
        if not message:
            clientsocket.close()
            break
        print("received: " + str(message))
        email = '...'.encode()
        clientsocket.send(email)

if __name__ == "__main__":
=======
ADDR = '0.0.0.0'
PORT = 5000

BUFF_SIZE = 1024

connections = []

# public key : client
clients_DB = { 'Rytis' : '0123456', 'Karolis' : '0011223' }

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
>>>>>>> d99092215c2123c95d9090996e4d20f9a1c4cca0
    main()