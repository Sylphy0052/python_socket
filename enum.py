from enum import IntEnum
import sys

class Prototype(IntEnum):
    DTCP = 1
    DUDP = 2

def main():
    if len(sys.argv) != 2:
        print("Must 1 argument.")
        sys.exit()
    proto_type = int(sys.argv[1])
    if proto_type == Prototype.DTCP:
        print("DTCP")
    elif proto_type == Prototype.DUDP:
        print("DUDP")
    else:
        print("Error")

if __name__ == '__main__':
    main()
