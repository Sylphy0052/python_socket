# -*- coding: utf-8 -*-

from enum import IntEnum
import hashlib
import socket
import sys

class Dip():
    class Type(IntEnum):
        DTCP = 1
        DUDP = 2

    def __init__(self, proto_type, payload):
        self.proto_type = proto_type # 4byte
        self.version = 1 # 4byte
        self.ttl = 123456 # 4byte
        self.payload = payload

class Dtcp():
    def __init__(self, lentgh, payload):
        self.proto_type = 3 # 4byte
        self.length = length # 4byte
        self.digest = 0 # 16byte
        self.payload = payload

    def calc_digest():
        self.digest = hashlib.md5(self.payload.encode('utf-8')).hexdigest()

    def toByte():


class Dudp():
    def __init__(self, length, payload):
        self.proto_type = 3 # 4byte
        self.length = length # 4byte
        self.payload = payload

    def toByte():


def connect_sock():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 8000))
    return sock

def read_data(file_name):
    data_file = open(file_name, 'r')
    read_file = data_file.read()
    data = read_file.replace('\n', ' ')
    data_file.close()
    data_length = len(data.replace(' ', ''))
    return data_length, data

def send_msg(sock, msg):
    sock.send(msg.encode('utf-8'))
    sock.close()

def main():
    args = sys.argv
    if len(args) != 3:
        print(len(args))
        print("Invalid argument. Needs 2 arguments.")
        sys.exit()
    protocol_type, file_name = args[1], args[2]
    data_length, data = read_data(file_name)
    print("size:", data_length)
    send_msg(connect_sock(), data)

if __name__ == '__main__':
    main()
