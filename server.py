import socket

def main():
    host = '127.0.0.1'
    port = 5001

    s = socket.socket()
    s.bind((host, port))

    s.listen(1)

    c, addr = s.accept()

    print(f'Connection from {str(addr)}')

    while True:
        data = c.recv(1024)

        if not data:
            break

        print(f'From connected user {str(data)}')
        data = str(data).upper()
        print(f'Sending back: {str(data)}')
        c.send(data.encode())

    c.close()

if __name__ == '__main__':
    main()
