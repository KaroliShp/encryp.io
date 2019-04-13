#Imports Modules
import socket
import time

#Defines Server Values
HOST = ''
PORT = 5000

clients = []

max_connections = 10
IP = socket.gethostname() #Gets Hostname Of Current Macheine


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((HOST,PORT))
    except Exception as e:
        print("Binding error:" + str(e))

    s.setblocking(0)

    quitting = False
    print("Server started at " + IP + " on port " + str(PORT))

    #Opens Server
    s.listen(max_connections)
    # print("Server started at " + IP + " on port " + str(PORT))

    while not quitting:
        try:
            data, addr = s.recvfrom(1024)
            if "Quit" in str(data):
                quitting = True
            if addr not in clients:
                clients.append(addr)

            print(time.ctime(time.time) + str(addr) + ": :" + str(data))
            for client in clients:
                s.sendto(data, client)
        except Exception as e:
            # print(e)
            pass


# #Accepts Incomming Connection
# (clientsocket, address) = s.accept()
# print("New connection made!" + str(address) + "joins the call")

if __name__ == "__main__":
    main()