from socket import AF_INET, socket, SOCK_STREAM
import threading

HOST = '192.168.1.188'
PORT = 5001

BUFSIZ = 1024


def send_message(client_socket):
    while True:
        message = input('You: \n')
        client_socket.send(message.encode())

def main():
    print(f'Starting the client...')

    client_socket = socket(AF_INET, SOCK_STREAM)
    print(f'Client socket created successfully')

    client_socket.connect((HOST, PORT))
    print(f'Connected to: {HOST}:{str(PORT)}')

    send_thread = threading.Thread(target=send_message, args=(client_socket,))
    send_thread.daemon = True
    send_thread.start()

    while True:
        data = client_socket.recv(BUFSIZ).decode()

        if not data:
            break

        print(f'Received: {data}\nYou:')

if __name__ == '__main__':
    main()
