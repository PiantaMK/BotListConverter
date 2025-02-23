from src.utils.format import SteamID
from datetime import datetime

def adjust_priority(priority):
    if priority in [0, 1]:
        print("WARNING: Invalid priority assigned, changing to 2...")
        return 2
    return max(-1, min(10, priority))

def write_ids(ids, priority):
    return "".join(f'playerlist.SetPriority("{SteamID(i).id2}",{priority})\n' for i in ids)

def dict_len(d):
    lengths = {k: len(v) for k, v in d.items()}
    lengths["total"] = sum(lengths.values())
    return lengths

def ask_for_priorities(ids):
    if isinstance(ids, dict):
        priorities = {}
        for category in ids:
            priority = int(input(f"What priority do you want to assign for the '{category}' list? (-1 or 2-10): "))
            priorities[category] = priority
        return priorities
    else:
        return int(input(f"What priority do you want to assign for the list? (-1 or 2-10): "))

def format_lboxlua(ids, listname="Error"):

    priorities = ask_for_priorities(ids)

    now = datetime.now()
    ret =  f"---@diagnostic disable: undefined-global\n" # not actually needed
    ret += f"--[[ auto-priority script made by Pianta's BotListConverter ]]\n"
    ret += f"--[[ generated at {now.strftime('%d-%b-%y %a')} ]]\n"

    total_ids = 0

    if isinstance(ids, dict):
        ret += "\n"
        ln = dict_len(ids)
        for cat, count in ln.items():
            if cat == "total": # skip total count
                continue

            ret += f"-- {cat} has {count} IDs and priority {priorities[cat]}\n"
        ret += f"-- {ln['total']} IDs in total\n\n"
        for category, id_list in ids.items():
            priority = adjust_priority(priorities[category])
            ret += f"-- {category}\n\n"
            ret += write_ids(id_list, priority)
            ret += "\n"
            total_ids += len(id_list)
        ret += f"\nprint(\"{len(ids)} categories processed.\")\n"
    else:
        priority = adjust_priority(priorities)
        ret += f"\n-- {listname} has {len(ids)} IDs and priority {priority}\n\n"
        ret += write_ids(ids, priority)
        total_ids = len(ids)

    ret += f"\nprint(\"{total_ids} players added.\")"
    return ret

_ext = ".lua"
def _main(lst, listname):
    # supports dict
    return format_lboxlua(lst, listname)