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
        self.type = int(self.deserialize_data(datas[0:8]), 16) # 4byte
        self.version = int(self.deserialize_data(datas[8:16]), 16) # 4byte
        self.ttl = int(self.deserialize_data(datas[16:24]), 16) # 4byte
        self.payload = datas[24:]
        self.datas = datas
        # print(datas)
        # print(self.version)
        # print(self.ttl)
        # print(self.payload)

    def execute(self):
        # print(self.deserialize_data(self.payload))
        return self.payload

class Layer2(Layer):
    def __init__(self, datas):
        self.proto_type = int(self.deserialize_data(datas[0:8]), 16) # 4byte
        self.length = int(self.deserialize_data(datas[8:16]), 16) # 4byte
        self.digest = ''
        self.payload = []
        self.datas = datas
        # print('proto_type:', self.proto_type)
        # print('length:', self.length)

    def calc_digest(self):
        calc_payload = ''
        i = 0
        # print('calc_digest:', self.payload[12:])
        for data in self.payload[12:]:
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
        return hashlib.md5(calc_payload.encode('utf-8')).hexdigest()
        # print(self.digest)
        # print([int(i, 16) for i in self.digest])
        # return [int(i, 16) for i in self.digest]

    def check_header(self):
        if self.proto_type == 1: # DTCP
            self.digest = self.deserialize_data(self.datas[16:48])
            self.payload = self.datas[48:]
            # print('digest:', self.digest)
            # print('payload:', self.payload)
        elif self.proto_type == 2: # DUDP
            self.payload = self.datas[16:]
    def check_md5(self):
        if self.digest == self.calc_digest():
            # 成功
            print('Match MD5')
        else:
            # 失敗
            # print(self.digest)
            # print(self.calc_digest())
            print('Don\'t match MD5')
            sys.exit()

    def execute(self):
        self.check_header()
        if self.proto_type == 1: # DTCP
            self.check_md5()
        elif self.proto_type ==2: # DUDP
            pass
        else:
            print("Error: Invalid Protocol.")
            sys.exit()
        return self.payload


# class Dtcp(Layer2):
#     def __init__(self):
#         super().__init__(length, payload)
#         self.digest = 0 # 16byte
#
#     def calc_digest(self):
#         calc_payload = ''
#         i = 0
#         for data in self.payload[12:]:
#             if data == 0:
#                 if i % 2 == 0:
#                     calc_payload += '0' + str(hex(data)).lstrip('0x')
#                 else:
#                     calc_payload += '0'
#             else:
#                 calc_payload += str(hex(data)).lstrip('0x')
#             i = i + 1
#             if i % 2 == 0:
#                 i = 0
#                 calc_payload += ' '
#         self.digest = hashlib.md5(calc_payload.encode('utf-8')).hexdigest()
#         print(self.digest)
#         print([int(i, 16) for i in self.digest])
#         return [int(i, 16) for i in self.digest]
#
#
#     def convert_header_to_byte(self):
#         self.calc_digest()
#         header = []
#         header += self.convert_byte(self.proto_type, 4)
#         header += self.convert_byte(self.length, 4)
#         header += self.calc_digest()
#         return header
#
# class Dudp(Layer2):
#     def __init__(self, length, payload):
#         super().__init__(length, payload)
#
#     def convert_header_to_byte(self):
#         header = []
#         header += self.convert_byte(self.proto_type, 4)
#         header += self.convert_byte(self.length, 4)
#         return header

def connect_sock():
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.bind(("localhost", 8000))
    serv_sock.listen(1)
    sock, addr = serv_sock.accept()
    print("Connected by " + str(addr))
    return sock

def receive_data(sock):
    datas = sock.recv(1060)
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

def main():
    recv_data = receive_data(connect_sock())
    # print(recv_data)
    protocol_type = deserialize_data(recv_data[0:4])
    # print(protocol_type)
    layer2_data = []
    layer1 = Layer2(recv_data)
    layer2_data = layer1.execute()
    layer3 = Dip(layer2_data)
    layer3_data = layer3.execute()

if __name__ == '__main__':
    while(True):
        main()
