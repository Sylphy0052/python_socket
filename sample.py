def convert_byte(data, num):
    print('convert_byte(', data, ',', num, ')')
    if data < 10: # 0~9
        print(data)
        byte = [data]
    elif data > 9: # A~F
        # print(hex(data))
        hex_data = hex(data).lstrip('0x')
        # print(hex_data)
        str_byte = hex_data
        # str_byte = hex(data)
        byte = [int(data, 16) for data in str_byte]
    while len(byte) != num:
        byte.insert(0, 0)
    return byte

proto_type = 12
version = 1
ttl = 12345
payload = [10, 10, 11, 11, 12, 12, 1, 1, 2, 2, 3, 3]

# hex_ttl = hex(ttl).lstrip('0x')

print(convert_byte(proto_type, 4))
