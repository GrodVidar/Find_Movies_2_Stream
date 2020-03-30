import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = input("enter host ip")

sock.connect((host, 1337))
while True:
    print(sock.recv(1024).decode("UTF-8"))
    sock.send(bytes(input("movie title:"), "UTF-8"))
    print(sock.recv(1024).decode("UTF-8"))
