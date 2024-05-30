ID64_MAGIC_NUMBER = 76561197960265728

def _format_ncc(string: str) -> str:
    return f"{string} - {string}"

def _format_cathook(string: str) -> str:
    return f"cat_pl_add_id {int(string) - ID64_MAGIC_NUMBER} RAGE"

def format_ncc_list(list: list) -> list:
    return [_format_ncc(i) for i in list]

def format_cathook_list(list: list) -> list:
    return [_format_cathook(i) for i in list]

def format_amalgam_list(list: list) -> str:
    formatted_list = ["{\n"]
    for i in list:
        formatted_list.append(f"""    "{int(i) - ID64_MAGIC_NUMBER}": [
        "Cheater"
    ]{"," if i != list[-1] else ""}\n""")
    formatted_list.append("}")
    return "".join(formatted_list)

def format_lbox_list(list: list, priority: int) -> str:
    if priority > 10:
        priority = 10
    if priority <= 1:
        priority = 2
    ret = ""
    for i in list:
        ret += f"{dec_to_hex(int(i) - ID64_MAGIC_NUMBER)};{priority};"
    return ret


def dec_to_hex(num):
    hex_str = hex(num)[2:]
    return hex_str