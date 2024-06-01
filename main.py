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
argparser.add_argument("-f", "--format", help="The output format.", choices=["ncc", "lbox", "cathook", "amalgam"])
argparser.add_argument("-o", "--output", help="The output file.", default="output.txt")
args = argparser.parse_args()

def save_formatted_list(ids, fmt, output, listname="bot"):
    if fmt == "ncc":
        formatted = format.format_ncc_list(ids)
    elif fmt == "cathook":
        formatted = format.format_cathook_list(ids)
    elif fmt == "lbox":
        priority = int(input(f"What priority do you want to assign for the {listname} list? (2-10): "))
        formatted = format.format_lbox_list(ids, priority)
    elif fmt == "amalgam":
        tag = input(f"What label do you want to assign to the {listname} list IDs? ")
        formatted = format.format_amalgam_list(ids, tag)
    else:
        raise ValueError(f"Unknown format: {fmt}")
    
    with open(output, "w") as f:
        f.write("\n".join(formatted) if isinstance(formatted, list) else formatted)
    print(f"Saved list to {output}")

def main(list=args.list, fmt=args.format, output=args.output):
    if list == "mcdb":
        ids_dict = megadb.fetch_mcdb()
        for category, ids in ids_dict.items():
            output_filename = f"{category}_{output}"
            save_formatted_list(ids, fmt, output_filename, category)
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

            save_formatted_list(ids, fmt, output)
        else:
            print(f"Error: {response.status_code}")

if __name__ == "__main__":
    main()
