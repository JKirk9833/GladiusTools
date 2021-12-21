from utils.parser import Parser
from utils.bectools.bec_unpacker import BecUnpacker
from utils.isotools.iso_unpacker import IsoUnpacker


def handle_echo(args):
    print(" ".join(args.text))


def handle_iso_unpack(args):
    if not args.output_dir.endswith("/"):
        raise RuntimeError("output_dir must end with /")
    handler = IsoUnpacker(args.file_path, args.output_dir, args.file_list)
    handler.unpack()


def handle_bec_unpack(args):
    if not args.output_dir.endswith("/"):
        raise RuntimeError("output_dir must end with /")
    handler = BecUnpacker(args.file_path, args.output_dir)
    handler.unpack()


if __name__ == "__main__":
    parser = Parser()

    if parser.args.command == "echo":
        handle_echo(parser.args)

    if parser.args.command == "unpack_iso":
        handle_iso_unpack(parser.args)

    if parser.args.command == "unpack_bec":
        handle_bec_unpack(parser.args)
