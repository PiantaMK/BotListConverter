import requests
import argparse
import os
from src.parsers import parser, megadb, groups
import src.format as format

argparse_example = \
"""
Example: python main.py -f amalgam -l cheater

Note: lbox_cfg and tf2bd are untested and may not work.
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
    choices=["bot", "cheater", "tacobot", "pazer", "mcdb", "groups", "sleepy-rgl", "sleepy-bot", "all"])

argparser.add_argument(
    "-f", "--format", 
    help="The output format.", 
    choices=["ncc", "lbox_cfg", "lbox_lua", "cathook", "amalgam", "tf2bd"])

argparser.add_argument(
    "-m", "--merge",
    help="Merge all steam groups into 1 list.",
    action="store_true")

args = argparser.parse_args()

def get_output_path(lst, ext, directory="output"):
    os.makedirs(directory, exist_ok=True)
    return f"{directory}/{lst}_output{ext}"

def get_pretty_name(lst):
    if lst == "bot":
        return "bots.tf - Bot"
    elif lst == "cheater":
        return "d3fc0n6 - Cheater"
    elif lst == "tacobot":
        return "d3fc0n6 - Tacobot"
    elif lst == "pazer":
        return "d3fc0n6 - Pazer"
    elif lst == "mcdb":
        return "megascatterbomb.com"
    elif lst == "groups":
        return "Steam Groups"
    elif lst == "sleepy-rgl":
        return "Sleepy List - RGL"
    elif lst == "sleepy-bot":
        return "Sleepy List - Bots"
    else:
        return lst
    
def get_extension(fmt):
    if fmt == "cathook":
        return ".cfg"
    elif fmt == "lbox_lua":
        return ".lua"
    elif fmt in ["amalgam", "tf2bd"]:
        return ".json"
    elif fmt == "ncc":
        return ".txt"
    elif fmt == "lbox_cfg":
        return ""  # no extension
    else:
        raise ValueError(f"Unknown format: {fmt}")

def fetch_and_parse(lst, is_all=False, mergedicts=False):
    if lst == "groups":
        if mergedicts:
            got = format.merge_dict_ids(groups.get(), "GROUPS")
        else:
            got = groups.get()
        return got
    elif lst == "mcdb":
        return megadb.fetch_mcdb()
    else: # TODO move this to a separate function
        url = parser.LISTS[lst]
        response = requests.get(url)
        if response.status_code == 200:
            if lst == "bot":
                ids = parser.parse_rijin_list(response.text)
            elif lst == "pazer":
                ids = parser.parse_pazer_list(response.text)
            elif lst in ["sleepy-rgl", "sleepy-bot"]:
                ids = parser.parse_tf2bd_list(response.text)
            else:
                ids = response.text.splitlines()
            return {get_pretty_name(lst): ids} if is_all else ids
        else:
            print(f"Error fetching '{get_pretty_name(lst)}': {response.status_code}")
            if lst == "bot":
                print("Trying fallback URL...")
                response = requests.get(parser.get_latest_archived_url(parser.LISTS[lst]))
                if response.status_code == 200:
                    ids = parser.parse_rijin_list(response.text)
                    return {get_pretty_name(lst): ids} if is_all else ids
                else:
                    print(f"Error fetching '{get_pretty_name(lst)}' with fallback URL: {response.status_code}")
            return {}

def save(ids, fmt, output, listname="Bot"):
    if isinstance(ids, list):
        ids = format.remove_duplicates(ids)
        if fmt == "ncc":
            formatted = format.format_ncc(ids)
        elif fmt == "cathook":
            formatted = format.format_cathook(ids)
        elif fmt == "lbox_cfg":
            priority = int(input(f"What priority do you want to assign for the '{listname}' list? (-1 or 2-10): "))
            formatted = format.format_lbox(ids, priority)
        elif fmt == "lbox_lua":
            priority = int(input(f"What priority do you want to assign for the '{listname}' list? (-1 or 2-10): "))
            formatted = format.format_lua(ids, priority, listname=listname)
        elif fmt == "amalgam":
            formatted = format.format_amalgam(ids, listname)
        elif fmt == "tf2bd":
            formatted = format.format_tf2bd(ids, listname)
        else:
            raise ValueError(f"Unknown format: {fmt}")
        
        with open(output, "w") as f:
            f.write("\n".join(formatted) if isinstance(formatted, list) else formatted)
        print(f"List saved to {output}")
    elif isinstance(ids, dict):
        ids = format.remove_duplicates(ids)

        if fmt == "amalgam":
            formatted_list = format.format_amalgam(ids)
            with open(output, "w") as f:
                f.write(formatted_list)
            print(f"List saved to {output}")

        elif fmt == "lbox_lua":
            priority_dict = {}
            for category in ids:
                priority = int(input(f"What priority do you want to assign for the '{category}' list? (-1 or 2-10): "))
                priority_dict[category] = priority
            formatted_list = format.format_lua(ids, priority_dict)
            with open(output, "w") as f:
                f.write(formatted_list)
            print(f"List saved to {output}")     
        else:
            for category, ids in ids.items():
                output_filename = get_output_path(category, get_extension(fmt))
                save(ids, fmt, output_filename, category)

def main(lst=args.list, fmt=args.format, merge=args.merge):
    if not lst or not fmt:
        print("Error: Missing arguments.\n")
        argparser.print_help()
        return
    ext = get_extension(fmt)
    if lst == "all":
        lists_to_fetch = ["bot", "cheater", "tacobot", "pazer", "mcdb", "groups", "sleepy-rgl", "sleepy-bot"]
        combined_dicts = []
        for l in lists_to_fetch:
            print(f"Fetching '{get_pretty_name(l)}'...")
            combined_dicts.append(fetch_and_parse(l, True, merge))
        merged_dict = format.merge_dicts(combined_dicts)
        save(merged_dict, fmt, get_output_path("all", ext))
    else:
        result = fetch_and_parse(lst, False, merge)
        if isinstance(result, dict):
            save(result, fmt, get_output_path(lst, ext))
        else:
            save(result, fmt, get_output_path(lst, ext), get_pretty_name(lst))

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    os.chdir(SCRIPT_DIR) # to make sure that all imports work

    main()