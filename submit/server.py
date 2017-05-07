# -*- coding: utf-8 -*-

import binascii
from enum import IntEnum
import hashlib
import multiprocessing
import socket
import sys
import threading
import time

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
        for data in datas:
            if int(data) < 10:
                str_data += str(data)
            else:
                str_data += hex(data).lstrip('0x')
        return str_data

class Dip(Layer):
    def __init__(self, datas):
        self.proto_type = int(self.deserialize_data(datas[0:8]), 16) # 4byte
        self.version = int(self.deserialize_data(datas[8:16]), 16) # 4byte
        self.ttl = int(self.deserialize_data(datas[16:24]), 16) # 4byte
        self.payload = datas[24:]
        self.datas = datas

    def execute(self):
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
        result = hashlib.md5(calc_payload.encode('utf-8')).hexdigest()
        self.digest = [int(i, 16) for i in result]
        return result

    def check_header(self):
        if self.protocol_type == 1: # DTCP
            self.digest = self.deserialize_data(self.datas[16:48])
            self.payload = self.datas[48:]
            self.check_md5()
        elif self.protocol_type == 2: # DUDP
            self.payload = self.datas[16:]
        else:
            print("Error: Invalid Protocol.")
            sys.exit()

    def check_md5(self):
        if self.digest == self.calc_digest():
            # 成功
            self.flg_md5 = True
        else:
            # 失敗
            self.flg_md5 = False

    def execute(self):
        self.check_header()
        return self.payload

def configure_sock():
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    serv_sock.bind(("localhost", 8080))
    serv_sock.listen(128)
    # sock, addr = serv_sock.accept()
    # print("Connected by " + str(addr))
    return serv_sock

def receive_data(datas):
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

def do_thread(data):
    recv_data = receive_data(data)
    layer2_data = []
    layer1 = Dip(recv_data)
    protocol_type, layer2_data = layer1.execute()
    print_layer1_info(layer1)
    layer2 = Layer2(layer2_data, protocol_type)
    layer2_data = layer2.execute()
    print_layer2_info(layer2)
    print_layer3_info(layer2_data)

def worker_thread(serv_sock):
    while True:
        clientsocket, (client_address, client_port) = serv_sock.accept()
        print('Connect: {0}:{1}'.format(client_address, client_port))

        while True:
            try:
                message = clientsocket.recv(2018)
                if message == b'':
                    continue
                print('Recv: from {0}:{1}'.format(client_address, client_port))
                do_thread(message)

            except OSError:
                break

            if len(message) == 0:
                break

            print('\n--- fin ---\nWaiting for connecting client...')

        clientsocket.close()
        print('Bye: {0}:{1}'.format(client_address, client_port))

def worker_process(serv_sock):
    NUMBER_OF_THREADS = 10
    for _ in range(NUMBER_OF_THREADS):
        thread = threading.Thread(target=worker_thread, args=(serv_sock,))
        thread.start()

    while True:
        time.sleep(1)

def main():
    serv_sock = configure_sock()
    NUMBER_OF_PROCESSES = multiprocessing.cpu_count()
    print('Waiting for connecting client...')
    for _ in range(NUMBER_OF_PROCESSES):
        process = multiprocessing.Process(target=worker_process, args=(serv_sock,))
        process.daemon = True
        process.start()

    while(True):
        time.sleep(1)

    serv_sock.close()

if __name__ == '__main__':
    main()
