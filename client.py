import socket

def main():
    host = '127.0.0.1'
    port = 5001

    s = socket.socket()
    s.connect((host, port))

    message = input("Input: ")
    while message != 'q':
        s.send(message.encode())
        data = s.recv(1024)
        print(f'Received from the server: {str(data)}')
        message = input("Input: ")
    s.close()

if __name__ == '__main__':
    main()
