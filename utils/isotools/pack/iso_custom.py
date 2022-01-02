from operator import attrgetter
from utils.helpers.file_helper import get_readable_size
from utils.helpers.iso_helper import IsoHelper
from utils.isotools.iso_rom_section import RomSection

# This is the Iso class that handles the packing process
class IsoCustom(IsoHelper):
    def __init__(self, fst_map):
        self.fst_map = fst_map
        self.rom_map = []

    def return_rom_map(self):
        output = ""
        for item in sorted(self.rom_map, key=attrgetter("file_id")):
            output += f"{hex(item.file_id)} {str(item.file_name)} {hex(item.file_start)} {hex(item.file_offset)}\n"

        return output
