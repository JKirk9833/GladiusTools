from textwrap import indent

from utils.helpers.file_helper import get_readable_size

# This class handles the creation of the new FST
# An extracted file system is a directory that contains all real and virtual files of
#   an ISO as single files in the local files system.
class FstDir:
    def __init__(self, name, flag, file_size=0, file_id=0):
        self.name = name  # Name of the directory - The root dir needs to be blank as per protocol
        self.lower = name  # Name of the directory lowercase
        self.flag = flag  # 0 for files / 1 for directories
        self.file_size = file_size
        self.file_id = file_id
        self.sub_dirs = []
        self.offset = 0

    # Need to spend some time deciphering the what and why's in this one
    # I think I need an explanation for this one
    def create(self, string_table_length, parent_id, own_id):
        # if "Unknown" in self.name:
        #     print(f"{self.name} {self.flag} {self.file_size} {self.file_id}")
        if self.file_id == -0x1:
            return ([], "")

        word_2 = 0
        word_3 = 0
        string = ""

        if self.name != "":
            string += self.name + "\0"
            if self.flag == 0:  # file
                word_2 = self.offset
                word_3 = self.file_size
            else:  # directory
                word_2 = parent_id
                word_3 = own_id + self.get_num_of_entries() + 1  # skip
        else:
            word_3 = self.get_num_of_entries() + 1  # skip

        # Why are we bit shifting this by 24? We're bitwise ORing the offset on
        fst = [self.flag << 24 | string_table_length, word_2, word_3]
        n = 0
        for item in self.sub_dirs:
            res = item.create(string_table_length + len(string), own_id, own_id + n + 1)
            fst += res[0]
            string += res[1]
            if res[1] != "":
                n += 1 + item.get_num_of_entries()

        return (fst, string)

    # This function takes a filename such as /data/movies/film.scn and rebuilds the file structure
    # e.g. FstDir("", 1).sub_dirs[0].name would be data, which in turn will contain movies
    def add_file_to_fst(self, file_name, file_size, file_id):
        # if "Unknown" in file_name:
        #     print(f"{file_name} {file_size} {file_id}")
        cur_dir = self
        name = file_name[1:]
        while name != "":  # Don't try to do this for root_dir or an invalid dir
            pos = name.find("/")  # Looks for indicator of a directory else returns -1
            if pos != -1:  # If -1 that means its a file
                cur_dir = cur_dir.add_sub_dir(name[0:pos])
                name = name[pos + 1 :]
            else:
                cur_dir.add_file(name, file_size, file_id)
                name = ""

    # Mass sets the offsets of all files within the ISO
    def set_offset_of_file(self, file_name, file_offset):
        cur_dir = self
        name = file_name[1:]

        while name != "":
            pos = name.find("/")
            if pos != -1:
                cur_dir = cur_dir.get_sub_dir(name[0:pos])
                name = name[pos + 1 :]
            else:
                cur_dir = cur_dir.get_sub_dir(name)
                return cur_dir.set_offset(file_offset)
        return 0

    # Prints the directory tree of the passed FstDir
    def print_dir_tree(self, fst_dir, iteration=0):
        cur_dir = fst_dir
        sub_dirs = sorted(cur_dir.sub_dirs, key=lambda x: x.flag, reverse=True)

        indent = "    " * iteration
        for item in sub_dirs:
            if item.flag == 0:  # If the FstDir is a file
                print(
                    f"{indent}~ {item.name} ({get_readable_size(item.file_size)}) Offset: {hex(item.offset)}"
                )
            if item.flag == 1:  # If the FstDir is a directory
                print(f"{indent}> {item.name}")
                self.print_dir_tree(item, iteration + 1)  # Print the directory

    # This function finds the file in the FstDir tree and sets the size
    def set_file_size(self, file_name, file_size):
        curDir = self
        name = file_name[1:]
        while name != "":
            pos = name.find("/")
            if pos != -1:
                curDir = curDir.get_sub_dir(name[0:pos])
                name = name[pos + 1 :]
            else:
                curDir = curDir.get_sub_dir(name)
                curDir = file_size
                return 1
        return 0

    # Gets an FstDir in a tree by name
    def get_sub_dir(self, name):
        for dir in self.sub_dirs:
            if dir.name == name:
                return dir
        return None

    # Gets an FstDir by name
    def add_sub_dir(self, name):
        sub_dir = self.get_sub_dir(name)
        if sub_dir == None:
            self.sub_dirs.append(FstDir(name, 1))
        self.sub_dirs = sorted(
            self.sub_dirs, key=lambda dir: dir.lower.replace("_", "}")
        )
        return self.get_sub_dir(name)

    # Gets an FstDir file by name
    def add_file(self, name, file_size, file_id):
        sub_dir = self.get_sub_dir(name)
        if sub_dir == None:
            self.sub_dirs.append(FstDir(name, 0, file_size, file_id))
        self.sub_dirs = sorted(
            self.sub_dirs, key=lambda dir: dir.lower.replace("_", "}")
        )
        return self.get_sub_dir(name)

    # Recursively checks all sub directories calc entries total
    def get_num_of_entries(self):
        nr = 0
        for i in self.sub_dirs:
            if i.file_id != -1:
                nr += 1
            nr += i.get_num_of_entries()
        return nr

    # Recursively checks through all sub directories to get the total length
    def get_length_of_strings(self):
        l = len(self.name) + 1
        for i in self.sub_dirs:
            if i.file_id != -1:
                l += i.get_length_of_strings()
        return l

    # Calculates the total size of the directory from this one
    def calc_size_of_fst(self):
        size = self.get_num_of_entries() * 0xC + 0xC
        size += self.get_length_of_strings()
        return size - 1  # subtract emptyChar of root_dir

    def set_offset(self, offset):
        self.offset = offset
        return offset + self.file_size


"""
  Alternative Source: https://wiki.gbatemp.net/wiki/NKit/Discs
  Since forum posts have a nasty habit of disappearing, I thought i'd copypasta and link the source
  SOURCE: https://gbatemp.net/threads/fst-bin-file-structure.78241/

  CONTENT - Tells you what an fst.bin file actually is and how it works

    The fst.bin file is divided into 2 parts, 1st is file entries & 2nd is filenames

    file entries
    each file entry is a 0xC segment
    (00) (filename offset 3Bytes) (offset>>2 4Bytes) (filesize 4Bytes)
    (01) (dir name offset 3Bytes) (parent entry # 4Bytes) (folder end entry 4Bytes)

    1st byte
    indicate whether it is a file or a folder, 00 for files and 01 for folders

    2nd - 4th bytes
    offset of the file/dir name from the start of the filenames segment (the starting address is mentioned below)

    5th - 8th bytes
    for files:
    It is the same offset you can see in trucha signer, but divided by 4 (>>2)
    (I dont know how to calculate whether a file is on the 1st or 2nd layer as there are more offsets involved)

    for dirs:
    It is the entry # of the parent directory, the 1st (ROOT) entry is entry #0
    so all 1st level dirs has the value of 0 on this location

    9th - 12th bytes
    for files:
    It is simply the size of the file.

    for dirs:
    It is the entry # of the last entry under the directory (including sub dirs & sub dir files)

    ROOT entry
    the fst.bin starts with the ROOT entry, it is slightly different from other dir entries

    01 | 00 00 00 | 00 00 00 00 | (Total number of entries 4Bytes)

    as the ROOT entry does not have a name nor a parent entry
    it always has the structure above
    therefore the filenames starts from: Total number of entries * 0xC

    filenames
    The filenames of each entry ends with a 0x00

    paddings
    the fst.bin is padded with 0x00 to 4bytes multiple

    (the presentation could be much better if this forum support tables)
"""
