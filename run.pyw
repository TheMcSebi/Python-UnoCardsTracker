from uno.uno import Uno
from argparse import ArgumentParser

if __name__ == "__main__":
    parser = ArgumentParser(description="Uno game")
    parser.add_argument("--fullscreen", help="Enable fullscreen mode")
    args = parser.parse_args()
    fullscreen = False
    if args.fullscreen:
        fullscreen = True
    Uno(fullscreen).main_loop()