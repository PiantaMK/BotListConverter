from utils.format import SteamID

def format_ncc(list: list) -> list:
    return [f"{SteamID(i).id64} - {SteamID(i).id64}" for i in list]

_ext = ".txt"
def _main(lst, listname):
    # does not support dict
    if isinstance(lst, list):
        return format_ncc(lst)
    else:
        for category in lst:
            lst[category] = format_ncc(lst[category])
        return lst