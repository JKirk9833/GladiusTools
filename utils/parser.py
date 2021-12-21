import argparse

# This class handles the creation and parsing of arguments for the application
class Parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.args = self.build()

    def build(self):
        sp = self.parser.add_subparsers(dest="command")

        self.init_echo(sp)
        self.init_unpack_iso(sp)
        self.init_unpack_bec(sp)

        return self.parser.parse_args()

    def init_echo(self, sp):
        echo = sp.add_parser(
            "echo", help="echo will print all following text to the console"
        )
        echo.add_argument(
            "text",
            action="store",
            nargs="+",
            type=str,
            help="Text to print to the console",
        )

    def init_unpack_iso(self, sp):
        unpack_iso = sp.add_parser("unpack_iso", help="Unpacks files from an iso")
        unpack_iso.add_argument(
            "unpack_iso",
            action="store_true",
            help="Unpacks files from an iso",
        )
        unpack_iso.add_argument(
            "--output_dir",
            nargs="?",
            type=str,
            action="store",
            default="./gladiusVANILLA/",
            help="Default: ./gladiusVANILLA/",
        )
        unpack_iso.add_argument(
            "--file_path",
            nargs="?",
            type=str,
            action="store",
            default="./gladiusVANILLA.iso",
            help="Default: ./gladiusVANILLA.iso",
        )
        unpack_iso.add_argument(
            "--file_list",
            nargs="?",
            type=str,
            action="store",
            default="gladiusVANILLA_FileList.txt",
            help="Default: gladiusVANILLA_FileList.txt",
        )

    # TODO - Finish this
    def init_pack_iso(self, sp):
        pack_iso = sp.add_parser(
            "pack_iso", help="Packs a valid folder into an iso file"
        )
        pack_iso.add_argument(
            "--input_dir",
            nargs="?",
            type=str,
            action="store",
            default="./gladiusVANILLA/",
            help="Default: ./gladiusVANILLA/",
        )
        pack_iso.add_argument(
            "--fst_bin",
            nargs="?",
            type=str,
            action="store",
            default="./gladiusVANILLA/fst.bin",
            help="Default: ./gladiusVANILLA/fst.bin",
        )
        pack_iso.add_argument(
            "--fst_map",
            nargs="?",
            type=str,
            action="store",
            default="./gladiusVANILLA/fst.bin",
            help="Default: ./gladiusVANILLA/fst.bin",
        )

    # TODO - update default values of filepath and outputdir paths
    def init_unpack_bec(self, sp):
        unpack_bec = sp.add_parser(
            "unpack_bec", help="Unpacks files from a bec-archive"
        )
        unpack_bec.add_argument(
            "unpack_bec",
            action="store_true",
            help="Unpacks files from a bec-archive",
        )
        unpack_bec.add_argument(
            "--output_dir",
            nargs="?",
            type=str,
            action="store",
            default="./",
            help="Default: ./",
        )
        unpack_bec.add_argument(
            "--file_path",
            nargs="?",
            type=str,
            action="store",
            default="./gladiusVANILLA.iso",
            help="Default: ./gladiusVANILLA.iso",
        )
