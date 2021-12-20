from utils.isotools.iso import Iso
from utils.helpers.file_helper import align_adr
from utils.helpers.type_helper import read_byte, read_unk_string, read_word
from utils.isotools.iso_dir_name import DirName

# TODO - finish the unpacking process, there's still shit in there
# TODO - Refactor the code handling url processing in write_basic_data
# All code that pertains to the iso unpacking process stored here
# https://discourse.world/h/2017/07/24/Gamecube-file-system-device
class IsoUnpacker:
    def __init__(self, file_path, output_dir, filelist):
        self.file_path = file_path
        self.output_dir = output_dir
        self.file_list = filelist
        self.dir_list = []

    # The function that does everything, just use this please
    def unpack(self):
        iso = Iso(self.file_path)
        header_output = iso.get_basic_headers()

        print(f"Game Info\n{header_output}\nBeginning write process...")

        # All file extraction happens here
        iso.write_and_store(self.output_dir, "boot.bin", 0x0, 0x440)
        iso.write_and_store(self.output_dir, "bi2.bin", 0x440, 0x2000)
        self.write_apploader(iso)
        self.write_fst(iso)
        header_output += self.write_dol(iso)
        header_output += f"{self.write_basic_data(iso)}\n\n"

        header_output += iso.dump_unknown_sections(self.output_dir)

    # GameCube apploader info: https://www.gc-forever.com/wiki/index.php?title=Apploader
    # I don't fully understand the below and it's difficult to locate
    # information about it (go figure, everything about this has that in common)
    def write_apploader(self, iso):
        loader_size = read_word(iso.file, 0x2440 + 0x14)  # Apploader Size
        loader_size += read_word(iso.file, 0x2440 + 0x18)  # Trailer Size
        loader_end = align_adr(0x2440 + loader_size, 0x100)
        iso.write_to_file(self.output_dir, "appldr.bin", 0x2440, loader_size)
        iso.add_rom_section("/appldr.bin", 0x2440, loader_end - 0x2440)

    # fst.bin contains the list of all files in the iso - woah :O
    def write_fst(self, iso):
        fst_start = read_word(iso.file, 0x424)
        fst_offset = read_word(iso.file, 0x428)
        iso.write_to_file(self.output_dir, "fst.bin", fst_start, fst_offset)
        iso.add_rom_section("/fst.bin", fst_start, fst_offset)

    # bootfile.dol: http://wiki.tockdom.com/wiki/DOL_(File_Format)
    def write_dol(self, iso):
        output = "\n"
        dol_start = read_word(iso.file, 0x420)

        # TODO - refactor this into something that doesn't look like doodoo
        text_pos = []
        text_mem = []
        text_size = []
        data_pos = []
        data_mem = []
        data_size = []
        tot_size = 0x100

        # Get all 7 text sections and add calculated size to total size
        for i in range(6):
            text_pos += [read_word(iso.file, dol_start + 0x0 + 0x4 * i)]
            text_mem += [read_word(iso.file, dol_start + 0x48 + 0x4 * i)]
            text_size += [read_word(iso.file, dol_start + 0x90 + 0x4 * i)]
            tot_size += text_size[i]

        # Get all 11 data sections and add calc'd size to total
        for i in range(10):
            data_pos += [read_word(iso.file, dol_start + 0x1C + 0x4 * i)]
            data_mem += [read_word(iso.file, dol_start + 0x64 + 0x4 * i)]
            data_size += [read_word(iso.file, dol_start + 0xAC + 0x4 * i)]
            tot_size += data_size[i]

        for i in range(10):
            output += (
                "Data "
                + hex(data_pos[i])
                + ":   "
                + hex(data_mem[i])
                + " - "
                + hex(data_size[i])
                + "\n"
            )

        output += "\n"

        # TODO - merge the for loops together for performance yay smiley face
        # Write text sections to file
        for i in range(6):
            iso.write_and_store(
                self.output_dir + "code/",
                "Text_" + hex(text_mem[i]) + ".bin",
                dol_start + text_pos[i],
                text_size[i],
            )

        # Write data sections to file
        for i in range(10):
            iso.write_and_store(
                self.output_dir + "code/",
                "Data_" + hex(data_mem[i]) + ".bin",
                dol_start + data_pos[i],
                data_size[i],
            )

        tot_size = align_adr(tot_size, 0x100)  # WHAT IS IT DOING
        iso.write_to_file(self.output_dir, "bootfile.dol", dol_start, tot_size)

        return output

    # The majority of the files are written here
    # This includes gladius.bec and audio.bec
    def write_basic_data(self, iso):
        output = ""
        base_address = read_word(iso.file, 0x424)

        output += iso.get_root_dir(base_address)
        num_entries = read_word(iso.file, base_address + 0x8)
        for i in range(num_entries):
            file_offset = 0xC * i
            is_dir = read_byte(iso.file, base_address + file_offset) == 1

            if is_dir:
                self.add_dir(iso, base_address, file_offset, num_entries * 0xC)
            if not is_dir:
                self.write_simple_data_file(
                    iso,
                    base_address,
                    file_offset,
                    num_entries * 0xC,
                    self.get_dir_path(i),
                )

        return output

    # appends a directory to the dir_list
    def add_dir(self, iso, base_address, offset, string_table):
        offset_string = (
            (read_word(iso.file, base_address + offset + 0x0)) & 0xFFFFFF
        ) + string_table
        string = read_unk_string(iso.file, base_address + offset_string, 0x20)
        parent_offset = read_word(iso.file, base_address + offset + 0x4)
        next_offset = read_word(iso.file, base_address + offset + 0x8)

        if offset == 0:
            string = ""

        output = string

        # print(f"Dir at: {hex(base_address + offset_string)}")
        # print(f"offset: {hex(int(offset / 0xC))} (parent: {hex(parent_offset)}), (next: {hex(next_offset)}), {output}")
        self.dir_list.append(DirName(string, offset / 0xC, next_offset))
        return output

    def write_simple_data_file(self, iso, base_address, offset, string_table, path):
        offset_string = (
            (read_word(iso.file, base_address + offset + 0x0)) & 0xFFFFFF
        ) + string_table
        string = read_unk_string(iso.file, base_address + offset_string, 0x20)
        file_offset = read_word(iso.file, base_address + offset + 0x4)
        file_length = read_word(iso.file, base_address + offset + 0x8)
        if string == "":
            string = "Unknown_" + hex(file_offset) + ".bin"
        # print("file name at: " + hex(base_address + offset_string))

        iso.write_to_file(
            (self.output_dir + path.replace("//", "/")),
            string.replace("//", "/"),
            file_offset,
            file_length,
        )

        iso.add_rom_section(path + string, file_offset, file_length, offset / 0xC)

    def get_dir_path(self, file_id):
        string = ""
        for dir in self.dir_list:
            if (file_id >= dir.start) & (file_id < dir.end):
                string += dir.name + "/"
        return string
