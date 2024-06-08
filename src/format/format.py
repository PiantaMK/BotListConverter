ID64_MAGIC_NUMBER = 76561197960265728

def format_lbox_list(list: list, priority: int) -> str:
    if priority > 10:
        priority = 10
    if priority <= 1:
        priority = 2
    ret = ""
    for i in list:
        ret += f"{dec_to_hex(int(i) - ID64_MAGIC_NUMBER)};{priority};"
    return ret

def _format_lbox_lua(string: str, priority) -> str:
    return f"playerlist.SetPriority(\"{string}\", {priority})"

def format_lbox_lua(list: list, priority: int) -> str:
    if priority > 10:
        priority = 10
    if priority <= 1:
        priority = 2
    return [_format_lbox_lua(int(i) - ID64_MAGIC_NUMBER, priority) for i in list]

def dec_to_hex(num):
    hex_str = hex(num)[2:]
    return hex_str
