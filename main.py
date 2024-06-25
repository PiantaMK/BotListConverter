import requests
import argparse
import os
from src.parser import parser, megadb, groups
from src.format import format

argparse_example = """
Example:
    python main.py -f amalgam -l cheater -n "Cheater"
"""

argparser = argparse.ArgumentParser(
    description="A tool to convert ID lists from various sources to valid playerlists.", 
    epilog=argparse_example)

argparser.add_argument(
    "-l", "--list", 
    help="The list to download.", 
    choices=["bot", "cheater", "tacobot", "pazer", "mcdb", "groups", "all"])

argparser.add_argument(
    "-f", "--format", 
    help="The output format.", 
    choices=["ncc", "lbox_cfg", "lbox_lua", "cathook", "amalgam", "tf2bd"])

args = argparser.parse_args()

def get_pretty_name(lst):
    if lst == "bot":
        return "bots.tf - Bot"
    elif lst == "cheater":
        return "d3fc0n6 - Cheater"
    elif lst == "tacobot":
        return "d3fc0n6 - Tacobot"
    elif lst == "pazer":
        return "d3fc0n6 - Pazer"
    else:
        return lst

def get_output_path(list_name, fmt, ext, directory="output"):
    os.makedirs(directory, exist_ok=True)
    return f"{directory}/{list_name}_output{ext}"

def fetch_and_parse(list_name, is_all=False):
    if list_name == "groups":
        return groups.get()
    elif list_name == "mcdb":
        return megadb.fetch_mcdb()
    else:
        url = parser.LISTS[list_name]
        response = requests.get(url)
        if response.status_code == 200:
            if list_name == "bot":
                ids = parser.parse_rijin_list(response.text)
            elif list_name == "pazer":
                ids = parser.parse_pazer_list(response.text)
            else:
                ids = response.text.splitlines()
            return {get_pretty_name(list_name): ids} if is_all else ids
        else:
            print(f"Error fetching {list_name}: {response.status_code}")
            return {}

def merge_dicts(dicts):
    merged = {}
    for d in dicts:
        for key, value in d.items():
            if key in merged:
                merged[key].extend(value)
            else:
                merged[key] = value
    return merged

def save_list(ids, fmt, output, listname="Bot"):
    ids = format.remove_duplicates_list(ids)
    if fmt == "ncc":
        formatted = format.format_ncc_list(ids)
    elif fmt == "cathook":
        formatted = format.format_cathook_list(ids)
    elif fmt == "lbox_cfg":
        priority = int(input(f"What priority do you want to assign for the '{listname}' list? (-1 or 2-10): "))
        formatted = format.format_lbox_list(ids, priority)
    elif fmt == "amalgam":
        formatted = format.format_amalgam_list(ids, listname)
    elif fmt == "tf2bd":
        formatted = format.format_tf2bd_list(ids, listname)
    elif fmt == "lbox_lua":
        priority = int(input(f"What priority do you want to assign for the '{listname}' list? (-1 or 2-10): "))
        formatted = format.format_lua_list(ids, priority, is_dict=False, listname=listname)
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
                formatted_dict[int(i) - format.ID64_MAGIC_NUMBER] = [category]
        formatted_list = format.format_amalgam_dict(formatted_dict)
        with open(output, "w") as f:
            f.write(formatted_list)
        print(f"List saved to {output}")
    elif fmt == "lbox_lua":
        priority_dict = {}
        for category in ids_dict:
            priority = int(input(f"What priority do you want to assign for the '{category}' list? (-1 or 2-10): "))
            priority_dict[category] = priority
        formatted_list = format.format_lua_list(ids_dict, priority_dict, is_dict=True)
        with open(output, "w") as f:
            f.write(formatted_list)
        print(f"List saved to {output}")
    else:
        for category, ids in ids_dict.items():
            output_filename = get_output_path(category, fmt, get_extension(fmt))
            save_list(ids, fmt, output_filename, category)

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
        return ""  # No extension
    else:
        raise ValueError(f"Unknown format: {fmt}")

def main(list=args.list, fmt=args.format):
    ext = get_extension(fmt)
    if list == "all":
        lists_to_fetch = ["bot", "cheater", "tacobot", "pazer", "mcdb", "groups"]
        combined_dicts = []
        for l in lists_to_fetch:
            combined_dicts.append(fetch_and_parse(l, True))
        merged_dict = merge_dicts(combined_dicts)
        save_dict(merged_dict, fmt, get_output_path("all", fmt, ext))
    else:
        result = fetch_and_parse(list, False)
        if isinstance(result, dict):
            save_dict(result, fmt, get_output_path(list, fmt, ext))
        else:
            save_list(result, fmt, get_output_path(list, fmt, ext), get_pretty_name(list))

if __name__ == "__main__":
    main()
