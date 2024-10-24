import socket

# 2.2 udp client

HOST = "localhost"
PORT = 9001


def start_udp_client(message):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(message.encode('utf-8'), (HOST, PORT))
    print(f'Message was send')
    data, _ = client.recvfrom(1024)
    print(f"Recieved message from server: {data.decode('utf-8')}")
    client.close()


if __name__ == "__main__":
    message = input('Input message: ')
    start_udp_client(message)