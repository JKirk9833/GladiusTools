import operator
from utils.helpers.file_helper import align_adr, create_file, get_filesize
from utils.helpers.type_helper import read_hex_string, read_string, read_word
from utils.isotools.iso_rom_section import RomSection

# TODO - Add a verification function to handle the cases that the iso is not found / invalid
# This class should contain any specific functions pertaining to the iso itself
class Iso:
    def __init__(self, file_path):
        self.file = open(file_path, "rb+")
        self.file_path = file_path
        self.rom_map = []

    def write_and_store(self, output_dir, file_name, file_start, file_offset):
        self.write_to_file(output_dir, file_name, file_start, file_offset)
        self.add_rom_section("/" + file_name, file_start, file_offset)

    def write_to_file(self, output_dir, file_name, file_start, file_offset):
        print(f"Writing {file_name}...")
        self.file.seek(file_start)
        file_section = self.file.read(file_offset)
        write_path = output_dir + file_name

        create_file(write_path)
        f = open(write_path, "wb")
        f.write(file_section)
        f.close()

        # If file not writing properly uncomment the below and pray
        # print("Write section to file: " + write_path)
        return file_name

    def add_rom_section(self, file_name, file_start, file_offset, file_id=-1):
        if file_offset > 0:
            self.rom_map.append(RomSection(file_name, file_start, file_offset, file_id))
        return None

    # Writes the unknown bits into a bunch of nebulous .bin files
    def dump_unknown_sections(self, output_dir):
        output = ""
        old_address = 0

        self.rom_map.sort(key=operator.attrgetter("file_start"))
        for item in self.rom_map:
            if old_address != item.file_start:
                self.write_to_file(
                    output_dir,
                    f"Unknown_{hex(old_address)}.bin",
                    old_address,
                    item.file_start - old_address,
                )
                output += f"{hex(old_address)} /Unknown_{hex(old_address)}.bin {hex(int(-1))} {hex(item.file_start - old_address)}\n"
            output += f"{hex(item.file_start)} {str(item.file_name)} {hex(int(item.file_id))} {hex(item.file_offset)}\n"
            old_address = align_adr(item.file_start + item.file_offset, 4)

        return output

    # I have no idea why or how this does anything, needs more reading
    def get_root_dir(self, base_address):
        offset_string = (read_word(self.file, base_address + 0x0)) & 0xFFFFFF
        parent_offset = read_word(self.file, base_address + 0x4)
        num_entries = read_word(self.file, base_address + 0x8)
        return f"\nRootDir: + {hex(offset_string)} - {hex(parent_offset)} - {hex(num_entries)}"

    # It's just cleaner to get the header data here
    def get_basic_headers(self):
        return (
            f"{self.file_path}\n"
            f"FileSize: {hex(get_filesize(self.file))}\n"
            f"Game Code: {str(read_string(self.file, 0x0, 0x4))}\n"
            f"Maker Code: {str(read_string(self.file, 0x4, 0x2))}\n"
            f"DVD Magic Word: 0x{str(read_hex_string(self.file, 0x1C, 0x4))}\n"
            f"Game Name: {str(read_string(self.file, 0x20, 0x3E0))}\n"
            f"Apploader Entrypoint: {hex(read_word(self.file, 0x2440 + 0x10))}\n"
        )
