import requests
import argparse
from src.parser import parser, megadb
from src.format import format

argparse_example = """
Example:
    python main.py -l pazer -o pazer.txt
"""

argparser = argparse.ArgumentParser(description="A tool to convert d3fc0n6's lists to valid NCC playerlists.", epilog=argparse_example)
argparser.add_argument("-l", "--list", help="The list to convert.", choices=["bot", "mcdb", "cheater", "tacobot", "pazer"])
argparser.add_argument("-s", "--savemode", help="The save format.", choices=["playerlist", "lua"])
argparser.add_argument("-o", "--output", help="The output file.", default="output.txt")
args = argparser.parse_args()

def saveas_plist(ids_dict, output):
    formatted = ""
    for category, ids in ids_dict.items():
        priority = int(input(f"What priority do you want to assign for the {category} list? (2-10): "))
        formatted += format.format_lbox_list(ids, priority) + "\n"

    with open(output, "w") as f:
        f.write(formatted)
    print(f"List saved to {output}")

def saveas_lua(ids_dict, output):
    formatted = []
    for category, ids in ids_dict.items():
        priority = int(input(f"What priority do you want to assign for the {category} list? (2-10): "))
        formatted.extend(format.format_lbox_lua(ids, priority))

    with open(output, "w") as f:
        f.write("\n".join(formatted))
    print(f"List saved to {output}")

def main(list=args.list, output=args.output, smode=args.savemode):
    if list == "mcdb":
        ids_dict = megadb.fetch_mcdb()
        if smode == "playerlist":
            saveas_plist(ids_dict, output)
        else:
            saveas_lua(ids_dict, output)
    else:
        url = parser.LISTS[list]
        response = requests.get(url)
        if response.status_code == 200:
            if list == "bot":
                ids = parser.parse_rijin_list(response.text)
            elif list == "pazer":
                ids = parser.parse_pazer_list(response.text)
            else:
                ids = response.text.splitlines()

            ids_dict = {list: ids}  # wrap in a dict to reuse save functions
            if smode == "playerlist":
                saveas_plist(ids_dict, output)
            else:
                saveas_lua(ids_dict, output)
        else:
            print(f"Error: {response.status_code}")

if __name__ == "__main__":
    main()
