#Imports Modules
import socket
import time

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
    main()