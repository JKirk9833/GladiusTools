import struct

# Big endian unsigned int
def read_word(file, Offset):
    file.seek(Offset)
    data = file.read(4)
    (word,) = struct.unpack(">I", data)
    return word


# Little endian unsigned byte
def read_byte(file, Offset):
    file.seek(Offset)
    data = file.read(1)
    (word,) = struct.unpack("<B", data)
    return word


# Reads string... duh
def read_string(file, offset, size):
    file.seek(offset)
    string = ""
    for i in range(size):
        byte = bytearray(file.read(1))
        if byte[0] != 0:
            string += chr(byte[0])
    return string


# Reads string, breaks if 0x00 found
def read_unk_string(file, offset, size):
    file.seek(offset)
    string = ""
    bytes = bytearray(file.read(size))
    for i in range(size):
        if bytes[i] != 0:
            string += chr(bytes[i])
        else:
            break
    return string


def read_hex_string(file, offset, size):
    file.seek(offset)
    string = ""
    for i in range(size):
        byte = bytearray(file.read(1))
        string += "%02x" % byte[0]  # {:02x}'.format(byte[0])
    return string
