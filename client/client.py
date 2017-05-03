# -*- coding: utf-8 -*-

import socket

def add_dipheader():

def connect_sock():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 8000))
    return sock

def read_data():
    data_file = open('text.txt', 'r')
    read_file = data_file.read()
    data = read_file.replace('\n', ' ')
    data_file.close()
    data_length = len(data.replace(' ', ''))
    return data_length, data

def send_msg(sock, msg):
    sock.send(msg.encode('utf-8'))
    sock.close()

def main():
    data_length, data = read_data()
    print(data_length)
    send_msg(connect_sock(), data)

if __name__ == '__main__':
    main()
