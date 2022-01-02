from struct import pack
from os import path
from utils.helpers.file_helper import align_adr, align_file_size, create_file
from utils.isotools.pack.fst_dir import FstDir
from utils.isotools.pack.iso_custom import IsoCustom


class IsoPacker:
    def __init__(self, input_dir, fst_bin, fst_map, output_file):
        self.input_dir = input_dir
        self.fst_bin = fst_bin
        self.fst_map = fst_map
        self.output_file = output_file
        self.root_dir = FstDir("", 1)

    def pack(self):
        output = ""
        iso = IsoCustom(self.fst_map)
        self.create_basic_layout(iso)
        self.set_all_file_offsets()
        self.root_dir.print_dir_tree(self.root_dir)
        output += iso.return_rom_map()
        new_fst = self.root_dir.create(0, 0, 0)
        print(new_fst)
        self.write_fst(
            new_fst
        )  # BUG IS HERE, edits the fst when packing and populates it with garbage from above somewhere
        self.write_iso_image()

    # Generates the directory tree (FstDir sub_dirs)
    def create_basic_layout(self, iso):
        file_list_txt = open(self.fst_map)
        for line in file_list_txt:
            words = line.split()  # file_start, path+name, file_offset, file_id
            if len(words) == 4:  # If the line is a valid file
                file_path = self.input_dir + words[1]
                file_offset = path.getsize(file_path)
                iso.add_rom_section(
                    words[1], int(words[0], 16), file_offset, int(words[3], 16)
                )
                self.root_dir.add_file_to_fst(words[1], file_offset, int(words[3], 16))
        self.root_dir.set_file_size(
            "/fst.bin", align_adr(self.root_dir.calc_size_of_fst(), 4)
        )

    # Assigns an offset to each file listed in the filelist
    def set_all_file_offsets(self):
        file_list_txt = open(self.fst_map)
        offset = 0
        for line in file_list_txt:
            words = line.split()  # file_start, path+name, file_offset, file_id
            if len(words) == 4:
                offset = self.root_dir.set_offset_of_file(words[1], offset)
                if (words[1] == "/appldr.bin") or (words[1] == "/bootfile.dol"):
                    offset = align_adr(offset, 0x100)
                offset = align_adr(offset, 4)

    def write_fst(self, new_fst):
        create_file(self.fst_bin)
        output_fst = open(self.fst_bin, "wb")
        for i in new_fst[0]:
            byte1 = i & 0xFF
            byte2 = (i >> 8) & 0xFF
            byte3 = (i >> 16) & 0xFF
            byte4 = (i >> 24) & 0xFF
            temp = pack("BBBB", byte4, byte3, byte2, byte1)
            output_fst.write(temp)

        output_fst.write(bytearray(new_fst[1], "utf8"))
        output_fst.close()

    def write_iso_image(self):
        file_list_txt = open(self.fst_map)
        create_file(self.output_file)
        output_rom = open(self.output_file, "wb")

        bootfile_offset = 0
        fst_offset = 0

        # Get each file listed in the filemap and write it to the iso
        for line in file_list_txt:
            words = line.split()  # file_start, path+name, file_offset, file_id
            if len(words) == 4:
                path = f"{self.input_dir}{words[1]}".replace("//", "/")
                print(f"Writing {path}...")
                part = bytearray(open(path, "rb").read())

                if words[1] == "/bootfile.dol":
                    bootfile_offset = output_rom.tell()
                    print(f"Bootfile Offset: {hex(bootfile_offset)}")
                elif words[1] == "/fst.bin":
                    fst_offset = output_rom.tell()
                    print(f"Fst Offset: {fst_offset}")

                output_rom.write(part)

                if (words[1] == "/appldr.bin") or (words[1] == "/bootfile.dol"):
                    align_file_size(output_rom, output_rom.tell(), 0x100)
                else:
                    align_file_size(output_rom, output_rom.tell(), 0x4)
        output_rom.seek(0x420)
        output_rom.write(pack(">II", int(bootfile_offset), int(fst_offset)))
