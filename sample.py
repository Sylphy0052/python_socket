import binascii

file_name = "text.txt"
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
print(byte_datas, '\n', data_length)

send_data = ''
for data in byte_datas:
    print(hex(data))
    print(str(hex(data)).lstrip('0x'))
    # send_data += hex(data)
print(send_data.encode('utf-8'))
