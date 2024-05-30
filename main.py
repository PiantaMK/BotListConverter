import requests
import argparse
from src.parser import parser
from src.format import format

argparse_example = """
Example:
    python main.py -l pazer -o pazer.txt
"""

argparser = argparse.ArgumentParser(description="A tool to convert d3fc0n6's lists to valid NCC playerlists.", epilog=argparse_example)
argparser.add_argument("-l", "--list", help="The list to convert.", choices=["bot", "cheater", "tacobot", "pazer"])
argparser.add_argument("-f", "--format", help="The output format.", choices=["ncc", "lbox", "cathook", "amalgam"])
argparser.add_argument("-o", "--output", help="The output file.", default="output.txt")
args = argparser.parse_args()

def main(list = args.list, fmt = args.format, output = args.output):
    url = parser.LISTS[list]
    response = requests.get(url)
    if response.status_code == 200:
        if list == "bot":
            ids = parser.parse_rijin_list(response.text)
        elif list == "pazer":
            ids = parser.parse_pazer_list(response.text)
        else:
            ids = response.text.splitlines()

        if fmt == "ncc":
            formatted = format.format_ncc_list(ids)
            with open(output, "w") as f:
                f.write("\n".join(formatted))
        elif fmt == "cathook":
            formatted = format.format_cathook_list(ids)
            with open(output, "w") as f:
                f.write("\n".join(formatted))
        elif fmt == "lbox":
            priority = int(input("What priority do you want to assign for the bot list? (2-10): "))
            formatted = format.format_lbox_list(ids, priority)
            with open(output, "w") as f:
                f.write(formatted)
            print("Done! You have to paste in the playerlist code into your config yourself.")
        elif fmt == "amalgam":
            formatted = format.format_amalgam_list(ids)
            with open(output, "w") as f:
                f.write(formatted)
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    try: 
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        exit()
    except Exception as e:
        print(e)
        exit()