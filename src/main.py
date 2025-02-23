import os

from utils.module import fetch_modules
from utils import format as formatutils

FORMATS_R = fetch_modules(os.path.join(os.path.dirname(__file__), 'formats'))
LISTS_R = fetch_modules(os.path.join(os.path.dirname(__file__), 'lists'))

PRETTY_NAMES = {name: getattr(module, '_pretty', name) for name, module in LISTS_R}
EXTENSIONS = {name: getattr(module, '_ext', '') for name, module in FORMATS_R}

LISTS = [m[0] for m in LISTS_R] + ["all"]
FORMATS = [m[0] for m in FORMATS_R]

def get_output_path(lst, ext, directory="output"):
    os.makedirs(directory, exist_ok=True)
    return f"{directory}/{lst}_output{ext}"

def get_pretty_name(lst):
    return PRETTY_NAMES.get(lst, lst)
    
def get_extension(fmt):
    if fmt in EXTENSIONS:
        return EXTENSIONS[fmt]
    else:
        raise ValueError(f"Unknown format: {fmt}")

def fetch_ids(lst, is_all=False, mergedicts=False):

    selected = next((item for item in LISTS_R if item[0] == lst), None)
    if not selected:
        raise ValueError(f"List '{lst}' not found.")

    selected_name, selected_list = selected
    listdata = selected_list._main()

    if mergedicts and lst == "steam":
        listdata = formatutils.merge_dict_ids(listdata)

    if is_all and not isinstance(listdata, dict):
        return {get_pretty_name(lst): listdata}

    return listdata

def save(ids, fmt, output, listname="Bot"):
    ids = formatutils.remove_duplicates(ids)
    
    format_dict = {
        name[:-3] 
        if name.endswith('.py') else 
        name: module for name, module in FORMATS_R
    }
    
    if fmt not in format_dict:
        raise ValueError(f"Invalid format: {fmt}")

    selected_format = format_dict[fmt]
    formatted = selected_format._main(ids, listname)
    
    if isinstance(formatted, list):
        formatted = "\n".join(formatted)
        with open(output, "w") as f:
            f.write(formatted)
        print(f"List saved to {output}")
    elif isinstance(formatted, dict):
        for cat, ids in formatted.items():
            with open(get_output_path(cat, get_extension(fmt)), "w") as f:
                if isinstance(ids, str):
                    f.write(ids)
                else:
                    f.write("\n".join(ids))
            print(f"List saved to {cat}")
    elif isinstance(formatted, str):
        with open(output, "w") as f:
            f.write(formatted)
        print(f"List saved to {output}")

def main(lst, fmt, merge):
    ext = get_extension(fmt)
    if lst == "all":
        lists_to_fetch = [lst for lst in LISTS if lst not in ["all", "custom"]]

        combined_dicts = []
        for l in lists_to_fetch:
            print(f"Fetching '{get_pretty_name(l)}'...")
            combined_dicts.append(fetch_ids(l, True, merge))
        merged_dict = formatutils.merge_dicts(combined_dicts)
        save(merged_dict, fmt, get_output_path("all", ext))
    else:
        result = fetch_ids(lst, False, merge)
        if isinstance(result, dict):
            save(result, fmt, get_output_path(lst, ext))
        else:
            save(result, fmt, get_output_path(lst, ext), get_pretty_name(lst))