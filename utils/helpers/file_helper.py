import os
from utils.hashes.gcnamehashes import filenameHashes


# Try to retrieve filepath from hash list else return a random .bin
# If it's a .bin we have no clue what the shit that is
def get_filename(hashcode, count):
    if hashcode in filenameHashes:
        return filenameHashes[hashcode]
    else:
        return str(count) + ".bin"


def get_filesize(file):
    file.seek(0, os.SEEK_END)
    return file.tell()


# Create directories to facilitate file_path
# TODO - check if this should contain stuff to write to the file also
def create_file(file_path):
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))


# I think this is aligning memory but I honestly have no clue
# Feeling pretty out of my depth here lmao
# I'd guess that the conditional can equal 255 or 0
# We're then bitwise ANDing the address and subtracting the align_val
# I just don't know WHY we're doing this, what are the consequences of avoiding it?
def align_adr(addr, align_val):
    if (addr & (align_val - 1)) != 0:
        addr = addr & 0x100000000 - align_val
        addr += align_val
    return addr


# Fills any empty bytes with zeroes up to the alignment
def align_file_size(file, pos, alignment):
    target = (pos + alignment - 1) & (0x100000000 - alignment)
    amount = target - pos
    file.write(b"\0" * amount)


# Returns a string containing a human-readable file size
def get_readable_size(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"
