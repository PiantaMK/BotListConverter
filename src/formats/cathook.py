from src.utils.format import SteamID

def format_cathook(list: list) -> list:
    return [f"cat_pl_add_id {SteamID(i).id3} RAGE" for i in list]

_ext = ".cfg"
def _main(lst, listname):
    # does not support dict
    if isinstance(lst, list):
        return format_cathook(lst)
    else:
        for category in lst:
            lst[category] = format_cathook(lst[category])
        return lst