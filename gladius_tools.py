from utils.parser import Parser

# 99% of this code belongs to Xexu and JimB16, I wrote very little original code
# The idea of this little project is just to educate myself on how to do this stuff in Python
# To make things simpler I've only supported the GC version as that seems to be the easiest to mod


def handle_echo(args):
    print(" ".join(args.echo))


if __name__ == "__main__":
    parser = Parser()

    if parser.args.echo:
        handle_echo(parser.args)
