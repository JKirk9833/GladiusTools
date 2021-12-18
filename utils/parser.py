import argparse


class Parser:
    def __init__(self):
        self.args = self.build()

    def build(self):
        parser = argparse.ArgumentParser()
        group = parser.add_mutually_exclusive_group(required=True)

        # Commands to parse here
        self.init_debug_commands(group)

        return parser.parse_args()

    # Commands written for playing with argparse
    def init_debug_commands(self, group):
        group.add_argument(
            "-echo",
            action="store",
            nargs="+",
            type=str,
            metavar=("text"),
            help="Test command written to play around with argparse",
        )
