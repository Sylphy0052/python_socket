# -*- coding: utf-8 -*-

import socket

def connect_sock():
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.bind(("localhost", 8000))
    serv_sock.listen(1)
    sock, addr = serv_sock.accept()
    print("Connected by " + str(addr))
    return sock

def receive_data(sock):
    data = sock.recv(1024)
    print("Client > ", data)
    sock.close()

def main():
    receive_data(connect_sock())

if __name__ == '__main__':
    main()
