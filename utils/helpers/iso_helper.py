from utils.isotools.iso_rom_section import RomSection


class IsoHelper:
    def add_rom_section(self, file_name, file_start, file_offset, file_id=-1):
        if file_offset > 0:
            self.rom_map.append(RomSection(file_name, file_start, file_offset, file_id))
        return None
