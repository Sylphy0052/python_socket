# -*- coding: utf-8 -*-

import binascii
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

class Dudp():
    def __init__(self, length, payload):
        self.proto_type = 3 # 4byte
        self.length = length # 4byte
        self.payload = payload

    def toByte():
        pass

def connect_sock():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 8000))
    return sock

def read_data(file_name):
    data_file = open(file_name, 'r')
    read_file = data_file.read()
    datas = read_file.replace('\n', ' ')
    datas = datas.split(' ')
    str_datas = []
    str_datas += [data for data in datas]
    byte_datas = []
    for str_data in str_datas:
        byte_datas += [int(byte_data, 16) for byte_data in str_data]
    data_file.close()
    data_length = len(byte_datas)
    return data_length, byte_datas

def send_msg(sock, msg):
    print(msg)
    send_data = ''
    i = 0
    for data in msg:
        send_data += str(hex(data)).lstrip('0x')
        i = i + 1
        if i % 2 == 0:
            i = 0
            send_data += ' '
    sock.send(send_data.encode('utf-8'))
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
