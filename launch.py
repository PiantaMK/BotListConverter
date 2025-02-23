import argparse
import os, sys

ARGS_DEBUG = 0

# to make sure that all imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
# os.chdir(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import LISTS, FORMATS, main

argparse_example = \
"""
Example: python main.py -f amalgam -l cheater

Note: lbox_cfg and tf2bd formats are untested and may not work.
"""

argparse_desc = \
"""
BotListConverter - a tool to convert ID lists from various sources to valid playerlists.


Made by PiantaMK - Download at github.com/PiantaMK/BotListConverter
Thanks to:
- Leadscales - for making the original version of this tool. (https://github.com/leadscales)
- Surepy/sleepy - for the base of the MCDB parser. (https://github.com/surepy)

"""

argparser = argparse.ArgumentParser(
    description=argparse_desc, 
    epilog=argparse_example,
    formatter_class=argparse.RawTextHelpFormatter)

argparser.add_argument(
    "-l", "--list", 
    help="The list to download.", 
    choices=LISTS)

argparser.add_argument(
    "-f", "--format", 
    help="The output format.", 
    choices=FORMATS)

argparser.add_argument(
    "-m", "--merge",
    help="Merge all steam groups into 1 list.",
    action="store_true")

args = argparser.parse_args()

_list = args.list
format = args.format
merge = args.merge

if not _list or not format:
    print("Error: Missing arguments.\n")
    argparser.print_help()
    exit()

if ARGS_DEBUG and (not args.list or not args.format):
    print("----- ARGS DEBUG -----")
    _list = input("Enter list name: ")
    format = input("Enter format: ")
    if _list == "steam":
        merge = input("Merge steam groups? (y/n): ").lower() == "y"
main(_list, format, merge)