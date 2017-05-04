import hashlib


f = open('text.txt', 'r')
read_file = f.read()
data = read_file.replace('\n', ' ')
f.close()
value = hashlib.md5(data.encode('utf-8')).hexdigest()
print(value.encode('utf-8'))
print(len(value))
