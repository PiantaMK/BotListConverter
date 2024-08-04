import json, re

LISTS = {
    "bot" : "https://api.bots.tf/rawtext", # Needs to be converted to 64 IDs and cleaned up
    "cheater" : "https://raw.githubusercontent.com/d3fc0n6/CheaterList/main/CheaterFriend/64ids",
    "tacobot" : "https://raw.githubusercontent.com/d3fc0n6/TacobotList/master/64ids",
    "pazer" : "https://raw.githubusercontent.com/d3fc0n6/PazerList/master/list.cfg", # Needs to be converted to 64 IDs and cleaned up
    "sleepy-rgl": "https://raw.githubusercontent.com/surepy/tf2db-sleepy-list/main/playerlist.rgl-gg.json" # Needs to be converted to 64 IDs
}

ID64_MAGIC_NUMBER = 76561197960265728

PAZER_REGEX = re.compile(r"\d+")

def to_64(id: int) -> int:
    return id + ID64_MAGIC_NUMBER

def parse_bot_list(list: str) -> str:
    list = list.splitlines()
    ids = []
    for i in list:
        ids.append(to_64(int(i)))
    return ids

def parse_rijin_list(list: str) -> str:
    list = list.splitlines()
    ids = []
    for i in list:
        ids.append(to_64(int(i[5:-1]))) # [U:X:YYYYY] -> YYYYY
    return ids

def parse_pazer_list(list: str) -> str:
    list = list.splitlines()
    ids = []
    for i in list:
        ids.append(to_64(int(PAZER_REGEX.search(i).group(0))))
    return ids

def parse_tf2bd_list(list: str) -> str:
    list = json.loads(list)
    ids = []
    for p in list['players']:
        sid = p['steamid']
        ids.append(to_64(int(sid[5:-1]))) # [U:1:YYYYY] -> YYYYY
    return ids