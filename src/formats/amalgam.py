from utils.format import SteamID

import json

def format_amalgam(data, tag="Bot"):
    if isinstance(data, list):
        adjusted_ids = {SteamID(i).id3: [tag] for i in data}
    elif isinstance(data, dict):
        adjusted_ids = {}
        for category, ids in data.items():
            for i in ids:
                adjusted_ids[SteamID(i).id3] = [category]
    else:
        raise ValueError("Input must be a list or dict")
    formatted_json = json.dumps(adjusted_ids, indent=4)
    return formatted_json

_ext = ".json"
def _main(lst, listname):
    return format_amalgam(lst, listname) # supports dict