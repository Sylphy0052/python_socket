f = open('text.txt', 'r')
read_file = f.read()
datas = read_file.replace('\n', ' ')
datas = datas.split(' ')
# print(datas)
str_list = []
# for data in datas:
#     str_list += data
str_list += [for data in datas]
print(str_list)
byte_array = []
# for str in str_list:
#     byte_array += int(str, 16)
for x in str_list:
    byte_array += [int(str, 16) for str in x]
print(byte_array)
# the_bytes_array = bytearray(blist)
# print(the_bytes_array)
f.close()
