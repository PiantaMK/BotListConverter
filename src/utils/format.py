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

class SteamID:
    ID64_BASE = 76561197960265728

    def __init__(self, value):
        self._account_id = None
        self._parse(value)

    def _parse(self, value):
        if value is None:
            raise ValueError("SteamID value cannot be None")
        
        val_str = str(value).strip()
        if not val_str:
            raise ValueError("SteamID value cannot be empty")

        if val_str.isdigit():
            val_int = int(val_str)
            if val_int >= self.ID64_BASE:
                self._account_id = val_int - self.ID64_BASE
            else:
                self._account_id = val_int
            return

        # Try Steam2: STEAM_X:Y:Z
        steam2_match = re.match(r"^STEAM_[0-5]:([0-1]):(\d+)$", val_str, re.IGNORECASE)
        if steam2_match:
            y = int(steam2_match.group(1))
            z = int(steam2_match.group(2))
            self._account_id = z * 2 + y
            return

        # Try Steam3 Bracket: [U:1:Y]
        steam3_match = re.match(r"^\[U:1:(\d+)\]$", val_str, re.IGNORECASE)
        if steam3_match:
            self._account_id = int(steam3_match.group(1))
            return

        # Try Steam3 No Bracket: U:1:Y
        steam3_nobrackets = re.match(r"^U:1:(\d+)$", val_str, re.IGNORECASE)
        if steam3_nobrackets:
            self._account_id = int(steam3_nobrackets.group(1))
            return

        raise ValueError(f"Invalid SteamID format: {value}")

    @property
    def id3(self):
        """Account ID / Steam3 number (e.g. 123456)"""
        return self._account_id

    @property
    def id3b(self):
        """Steam3 Bracket format (e.g. [U:1:123456])"""
        return f"[U:1:{self._account_id}]"

    @property
    def id64(self):
        """Steam64 / Community ID (e.g. 76561197960265728 + account_id)"""
        return self.ID64_BASE + self._account_id

    @property
    def id2(self):
        """Steam2 format (e.g. STEAM_0:X:Y)"""
        y = self._account_id % 2
        z = self._account_id // 2
        return f"STEAM_0:{y}:{z}"

    def __eq__(self, other):
        if isinstance(other, SteamID):
            return self._account_id == other._account_id
        try:
            return self._account_id == SteamID(other)._account_id
        except ValueError:
            return False

    def __hash__(self):
        return hash(self._account_id)

    def __repr__(self):
        return f"SteamID({self.id64})"

    def __str__(self):
        return str(self.id64)

def remove_duplicates(input_data):
    if isinstance(input_data, dict):
        return {key: list(set(value)) for key, value in input_data.items()}
    elif isinstance(input_data, list):
        return list(set(input_data))
    else:
        raise TypeError("Input must be a dict or list")
