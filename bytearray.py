import struct

# blist = [0, 0, 0, 1]
blist = []
blist += [0]
blist += [0]
blist += [0]
blist += [1]

# the_bytes = bytes(blist)
# print(the_bytes[:2])
the_bytes_array = bytearray(blist)
print(the_bytes_array)

a = struct.unpack('>L', the_bytes_array)
print(a)
