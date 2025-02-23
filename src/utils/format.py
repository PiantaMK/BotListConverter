import re

ID64_MAGIC_NUMBER = 76561197960265728

##### UTILS #####

def merge_dict_ids(d):
    merged_list = []
    for value in d.values():
        if isinstance(value, list):
            merged_list.extend(value)
        else:
            merged_list.append(value)
    
    return merged_list

def merge_dicts(dicts):
    merged = {}
    for d in dicts:
        for key, value in d.items():
            if key in merged:
                merged[key].extend(value)
            else:
                merged[key] = value
    return merged

def detect_id_type(id: str|int) -> str|None:
    if isinstance(id, int) or id.isdigit():
        if int(id) >= ID64_MAGIC_NUMBER:
            return "STEAMID64"
        else:
            return "STEAMID3-N"
    elif isinstance(id, str):
        if id.startswith("STEAM_0"):
            return "STEAMID2"
        elif id.startswith("[U:1:"):
            return "STEAMID3-B"
        else:
            return None
    else:
        return None

def cvt(id: str|int, tgt: str) -> str|int:
    idtype = detect_id_type(id)

    # no conversion needed
    if idtype == tgt:
        if idtype in ["STEAMID3-N", "STEAMID64"]:
            return int(id)
        return id
    
    id64 = None

    # convert to id64 (easier to convert)
    if idtype == "STEAMID2":
        m = re.search(r"STEAM_0:(\d):(\d+)", id)
        y = int(m.group(1))
        accnum = int(m.group(2))
        id64 = ID64_MAGIC_NUMBER + (2 * accnum) + y
    elif idtype == "STEAMID3-N":
        id64 = ID64_MAGIC_NUMBER + int(id)
    elif idtype == "STEAMID3-B":
        m = re.search(r"\[U:1:(\d+)\]", id)
        id64 = ID64_MAGIC_NUMBER + int(m.group(1))
    elif idtype == "STEAMID64":
        id64 = int(id)
    else:
        raise ValueError(f"Unknown ID type: {id}")

    id64 = int(id64)

    # convert to target format
    if tgt == "STEAMID2":
        account_id = id64 - ID64_MAGIC_NUMBER
        y = account_id % 2
        z = (account_id - y) // 2
        return f"STEAM_0:{y}:{z}"
    elif tgt == "STEAMID3-N":
        return id64 - ID64_MAGIC_NUMBER
    elif tgt == "STEAMID3-B":
        return f"[U:1:{id64 - ID64_MAGIC_NUMBER}]"
    elif tgt == "STEAMID64":
        return id64
    else:
        return None

class SteamID:
    def __init__(self, id):
        self._id = cvt(id, detect_id_type(id)) # so we can turn some formats into int
        self.id64 = cvt(id, "STEAMID64") # 76561197960389180
        self.id3 = cvt(id, "STEAMID3-N")  # 123456
        self.id3b = cvt(id, "STEAMID3-N") # [U:1:123456]
        self.id2 = cvt(id, "STEAMID2")  # STEAM_0:0:123456

def remove_duplicates(input_data):
    if isinstance(input_data, dict):
        return {key: list(set(value)) for key, value in input_data.items()}
    elif isinstance(input_data, list):
        return list(set(input_data))
    else:
        raise TypeError("Input must be a dict or list")
