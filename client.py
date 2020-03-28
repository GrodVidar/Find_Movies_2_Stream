import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(("127.0.0.1", 1337))
while True:
    print(sock.recv(1024).decode("UTF-8"))
    sock.send(bytes(input("movie title:"), "UTF-8"))
    print(sock.recv(1024).decode("UTF-8"))
