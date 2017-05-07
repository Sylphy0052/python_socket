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
        while len(byte) != num:
            byte.insert(0, 0)
        return byte

    def deserialize_data(self, datas):
        str_data = ''
        # print('data:', datas)
        for data in datas:
            if int(data) < 10:
                str_data += str(data)
            else:
                str_data += hex(data).lstrip('0x')
        # print(str_data)
        return str_data

class Dip(Layer):
    def __init__(self, datas):
        self.proto_type = int(self.deserialize_data(datas[0:8]), 16) # 4byte
        self.version = int(self.deserialize_data(datas[8:16]), 16) # 4byte
        self.ttl = int(self.deserialize_data(datas[16:24]), 16) # 4byte
        self.payload = datas[24:]
        self.datas = datas
        # print(datas)
        # print(self.version)
        # print(self.ttl)
        # print(self.payload)

    def execute(self):
        # print(self.payload)
        return self.proto_type, self.payload

class Layer2(Layer):
    def __init__(self, datas, protocol_type):
        self.proto_type = int(self.deserialize_data(datas[0:8]), 16) # 4byte
        self.length = int(self.deserialize_data(datas[8:16]), 16) # 4byte
        self.digest = ''
        self.payload = []
        self.datas = datas
        self.protocol_type = protocol_type
        self.flg_md5 = True
        # print('proto_type:', self.proto_type)
        # print('length:', self.length)

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
        # print('payload:', calc_payload)
        result = hashlib.md5(calc_payload.encode('utf-8')).hexdigest()
        self.digest = [int(i, 16) for i in result]
        return result
        # print(self.digest)
        # print([int(i, 16) for i in self.digest])
        # return [int(i, 16) for i in self.digest]

    def check_header(self):
        if self.protocol_type == 1: # DTCP
            self.digest = self.deserialize_data(self.datas[16:48])
            self.payload = self.datas[48:]
            # print(self.payload)
            self.check_md5()
            # print('digest:', self.digest)
            # print('payload:', self.payload)
        elif self.protocol_type == 2: # DUDP
            self.payload = self.datas[16:]
        else:
            print("Error: Invalid Protocol.")
            sys.exit()

    def check_md5(self):
        # print(self.digest)
        # print(self.calc_digest())
        if self.digest == self.calc_digest():
            # 成功
            # print('Match MD5')
            self.flg_md5 = True
        else:
            # 失敗
            # print(self.digest)
            # print(self.calc_digest())
            # print('Don\'t match MD5')
            self.flg_md5 = False
            # sys.exit()

    def execute(self):
        self.check_header()
        return self.payload

def connect_sock():
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.bind(("localhost", 8080))
    serv_sock.listen(1)
    sock, addr = serv_sock.accept()
    print("Connected by " + str(addr))
    return sock

def receive_data(sock):
    datas = sock.recv(2048)
    sock.close()
    datas = datas.decode('utf-8').split(' ')
    str_datas = []
    str_datas += [data for data in datas]
    byte_datas = []
    for str_data in str_datas:
        byte_datas += [int(byte_data, 16) for byte_data in str_data]
    return byte_datas

def deserialize_data(datas):
    str_data = ''
    for data in datas:
        if int(data) < 10:
            str_data += str(data)
        else:
            str_data += hex(data).lstrip('0x')
    # print(str_data)
    return int(str_data, 16)

def print_layer3_info(datas):
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
    if layer.flg_md5 == True:
        # 成功
        print('Match MD5')
    else:
        # 失敗
        print('Don\'t match MD5')
        sys.exit()

def print_layer1_info(layer):
    print('\n--- layer1 ---')
    print('type:', layer.proto_type)
    print('version: ', layer.version)
    print('ttl:', layer.ttl)

def main():
    recv_data = receive_data(connect_sock())
    # protocol_type = deserialize_data(recv_data[0:8])
    # print(protocol_type)
    layer2_data = []
    layer1 = Dip(recv_data)
    protocol_type, layer2_data = layer1.execute()
    print_layer1_info(layer1)
    layer2 = Layer2(layer2_data, protocol_type)
    layer2_data = layer2.execute()
    print_layer2_info(layer2)
    print_layer3_info(layer2_data)

def debug_print(datas):
    calc_payload = ''
    i = 0
    # print('calc_digest:', self.payload[12:])
    for data in datas:
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
    print('dbg: ', calc_payload)

if __name__ == '__main__':
    while(True):
        print('Waiting for connecting client...')
        main()
