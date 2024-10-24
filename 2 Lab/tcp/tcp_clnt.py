import socket

# 1.2 tcp client

HOST = 'localhost'
PORT = 9001


def start_client(message):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    print(f'Connected ')
    client.sendall(message.encode('utf-8'))
    data = client.recv(1024)
    print(f"Received message from server: {data.decode('utf-8')}")
    client.close()


if __name__ == "__main__":
    message = input('Input message: ')
    start_client(message)