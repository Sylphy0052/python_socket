f = open('text.txt', 'r')
read_file = f.read()
data = read_file.replace('\n', ' ')
print(data)
f.close()