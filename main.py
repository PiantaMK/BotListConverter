import requests
import argparse
from src.parser import parser, megadb, groups
from src.format import format

argparse_example = """
Example:
    python main.py -l pazer -o pazer.txt
"""

argparser = argparse.ArgumentParser(description="A tool to convert d3fc0n6's lists to valid NCC playerlists.", epilog=argparse_example)
argparser.add_argument("-l", "--list", help="The list to convert.", choices=["bot", "mcdb", "cheater", "tacobot", "pazer", "groups"])
argparser.add_argument("-f", "--format", help="The output format.", choices=["ncc", "lbox", "cathook", "amalgam", "tf2bd"])
argparser.add_argument("-n", "--namelabel", help="The list name for formats that support label names (e.g Amalgam). Does not affect MCDB.")
argparser.add_argument("-o", "--output", help="The output file.", default="output.txt")
args = argparser.parse_args()


def save_list(ids, fmt, output, listname="Bot"):
    ids = format.remove_duplicates_list(ids)
    if fmt == "ncc":
        formatted = format.format_ncc_list(ids)
    elif fmt == "cathook":
        formatted = format.format_cathook_list(ids)
    elif fmt == "lbox":
        priority = int(input(f"What priority do you want to assign for the '{listname}' list? (2-10): "))
        formatted = format.format_lbox_list(ids, priority)
    elif fmt == "amalgam":
        formatted = format.format_amalgam_list(ids, listname)
    elif fmt == "tf2bd":
        formatted = format.format_tf2bd_list(ids, listname)
    else:
        raise ValueError(f"Unknown format: {fmt}")
    
    with open(output, "w") as f:
        f.write("\n".join(formatted) if isinstance(formatted, list) else formatted)
    print(f"List saved to {output}")


def save_dict(ids_dict, fmt, output):
    ids_dict = format.remove_duplicates_dict(ids_dict)
    if fmt == "amalgam":
        formatted_dict = {}
        for category, ids in ids_dict.items():
            for i in ids:
                formatted_dict[int(i) - 76561197960265728] = [category]
        formatted_list = format.format_amalgam_dict(formatted_dict)
        with open(output, "w") as f:
            f.write(formatted_list)
        print(f"List saved to {output}")
    else:
        for category, ids in ids_dict.items():
            output_filename = f"{category}_{output}"
            save_list(ids, fmt, output_filename, category)


def main(list=args.list, fmt=args.format, output=args.output, name=args.namelabel):
    if list == "groups":
        ids = groups.get()
        save_dict(ids, fmt, output)
    elif list == "mcdb":
        ids = megadb.fetch_mcdb()
        save_dict(ids, fmt, output)
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

            save_list(ids, fmt, output, name)
        else:
            print(f"Error: {response.status_code}")

if __name__ == "__main__":
    main()
