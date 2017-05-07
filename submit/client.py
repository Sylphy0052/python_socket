# -*- coding: utf-8 -*-

import binascii
from enum import IntEnum
import hashlib
import socket
import sys

class Layer():
    class Type(IntEnum):
        DTCP = 1
        DUDP = 2

    def convert_byte(self, data, num):
        if int(data) < 10:
            byte = [int(data)]
        else:
            hex_data = hex(data).lstrip('0x')
            str_byte = hex_data
            byte = [int(data, 16) for data in str_byte]
        while len(byte) != num * 2:
            byte.insert(0, 0)
        return byte

    def execute(self):
        return self.convert_header_to_byte() + self.payload

class Dip(Layer):
    def __init__(self, proto_type, payload):
        self.proto_type = proto_type
        self.version = 1 # 4byte
        self.ttl = 12345 # 4byte
        self.payload = payload

    def convert_header_to_byte(self):
        header = []
        header += self.convert_byte(self.proto_type, 4)
        header += self.convert_byte(self.version, 4)
        header += self.convert_byte(self.ttl, 4)
        return header

class Layer2(Layer):
    def __init__(self, length, payload):
        self.length = length # 4byte
        self.payload = payload

class Dtcp(Layer2):
    def __init__(self, length, payload):
        super().__init__(length, payload)
        self.proto_type = 3
        self.digest = 0 # 16byte

    def calc_digest(self):
        calc_payload = ''
        i = 0
        for data in self.payload:
            if data == 0:
                if i % 2 == 0:
                    calc_payload += '0' + str(hex(data)).lstrip('0x')
                else:
                    calc_payload += '0'
            else:
                calc_payload += str(hex(data)).lstrip('0x')
            i = i + 1
            if i % 2 == 0:
                i = 0
                calc_payload += ' '
        self.digest = hashlib.md5(calc_payload.encode('utf-8')).hexdigest()
        self.digest = [int(i, 16) for i in self.digest]
        return self.digest


    def convert_header_to_byte(self):
        self.calc_digest()
        header = []
        header += self.convert_byte(self.proto_type, 4)
        header += self.convert_byte(self.length, 4)
        header += self.calc_digest()
        return header

class Dudp(Layer2):
    def __init__(self, length, payload):
        super().__init__(length, payload)
        self.proto_type = 3

    def convert_header_to_byte(self):
        header = []
        header += self.convert_byte(self.proto_type, 4)
        header += self.convert_byte(self.length, 4)
        return header

def connect_sock():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 8080))
    return sock

def print_layer3_info(datas, data_length):
    print('size:', data_length)
    print('\n--- layer3 ---')

    str_data = ''
    i = 0
    for data in datas:
        if data == 0:
            if i % 2 == 0:
                str_data += '0' + str(hex(data)).lstrip('0x')
            else:
                str_data += '0'
        else:
            str_data += str(hex(data)).lstrip('0x')
        i = i + 1
        if i % 2 == 0:
            str_data += ' '
        if i % 32 == 0:
            str_data += '\n'
            i = 0
    print(str_data)

def print_layer2_info(layer):
    print('\n--- layer2 ---')
    print('type:', layer.proto_type)
    print('len:', layer.length)
    digest = ''
    i = 0
    for data in layer.digest:
        if data == 0:
            digest += '0' + str(hex(data)).lstrip('0x')
        else:
            digest += str(hex(data)).lstrip('0x')
        i = i + 1
        if i % 2 == 0:
            digest += ' '
        if i % 32 == 0:
            digest += '\n'
            i = 0
    print('md5:', digest.rstrip('\n'))

def print_layer1_info(layer):
    print('\n--- layer1 ---')
    print('type:', layer.proto_type)
    print('version: ', layer.version)
    print('ttl:', layer.ttl)

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
    send_data = ''
    i = 0
    for data in msg:
        if data == 0:
            if i % 2 == 0:
                send_data += '0' + str(hex(data)).lstrip('0x')
            else:
                send_data += '0'
        else:
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
        print("Invalid argument. Needs 2 arguments.")
        sys.exit()
    protocol_type, file_name = int(args[1]), args[2]
    data_length, data = read_data(file_name)
    print_layer3_info(data, data_length)

    layer2_data = ''
    # if protocol_type == Layer.Type.DTCP: できない？
    if protocol_type == 1:
        layer2 = Dtcp(data_length, data)
        layer2_data = layer2.execute()
    # elif protocol_type == Layer.Type.DUDP: 同様
    elif protocol_type == 2:
        layer2 = Dudp(data_length, layer2_data)
        layer2_data = layer2.execute()
    print_layer2_info(layer2)

    layer1 = Dip(protocol_type, layer2_data)
    layer1_data = layer1.execute()
    print_layer1_info(layer1)
    send_msg(connect_sock(), layer1_data)

if __name__ == '__main__':
    main()
