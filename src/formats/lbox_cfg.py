from src.utils.format import SteamID

def format_lboxcfg(list: list, priority: int) -> str:
    if priority in [0, 1]:
        print("WARNING: Invalid priority assigned, changing to 2...")
        priority = 2
    priority = max(-1, min(10, priority))

    ret = "".join(f"{hex(SteamID(i).id3)[2:]};{priority};" for i in list)
    return ret

_ext = ""
def _main(lst, listname):
    # does not support dict
    if isinstance(lst, list):
        priority = int(input(f"What priority do you want to assign for the '{listname}' list? (-1 or 2-10): "))
        return format_lboxcfg(lst, priority)
    else:
        for category in lst:
            priority = int(input(f"What priority do you want to assign for the '{category}' list? (-1 or 2-10): "))
            lst[category] = format_lboxcfg(lst[category], priority)
        return lst #''.join(lst[category] for category in lst)