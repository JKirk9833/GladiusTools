import struct
import queue
from os.path import isfile
from collections import namedtuple
from utils.helper import format_named_tuple
from utils.helpers.file_helper import get_filename

# Constants
fileAtEnd = 0xC0000000
headerFile = "filelist.txt"
MAX_NR_OF_THREADS = 1
file_queue = queue.Queue()

# Unpacks the Gladius data.bec file and spits it out in the output_dir
class BecUnpacker:
    def __init__(self, file_path, output_dir):
        self.file_path = file_path
        self.output_dir = output_dir
        print("file_path: " + str(self.file_path))
        print("Output Directory: " + str(self.output_dir))

    # TODO - Check that the gladius ISO image is valid
    def verify_can_unpack(self):
        if not isfile(self.file_path):
            raise RuntimeError("Invalid .iso file path specified")

    def unpack(self):
        self.verify_can_unpack()
        file = open(self.file_path, "rb+")  # Opens file readonly as bytes
        self.split_rom(file)

    # Returns string of datalines
    def split_rom(self, file):
        output = ""
        bec_header = namedtuple(
            "bec_header", ["file_alignment", "num_of_files", "header_magic"]
        )

        file.seek(0x6)  # Skips past nebulous GLSE64 stamp
        data = file.read(10)  # Grabs BEC header
        # Header format:
        # < little endian (endianness is fucking bullshit btw, i know it can be faster but is it worth the complexity addition?)
        # H - unsigned short (2 bytes) - FileAlignment
        # I - unsigned int (4 bytes) - NrOfFiles / HeaderMagic
        header = bec_header._make(struct.unpack("<HII", data))
        print("Header Details: " + str(header))
        output += format_named_tuple(header)

        entry = namedtuple(
            "file_entry", ["path_hash", "data_offset", "comp_data_size", "data_size"]
        )
        # TODO - finish writing the RomSection class and extend .bex unpacker once ISO tool written
        for i in range(header.num_of_files):
            data = file.read(0x10)
            file_entry = entry._make(struct.unpack("<IIII", data))
            file_name = get_filename(file_entry.path_hash, i)
            if file_name == f"{i}.bin":
                print(f"{file_name} | {hex(file_entry.path_hash)}")
