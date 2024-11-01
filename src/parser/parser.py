import json, re
from ..format.format import cvt

LISTS = {
    "bot" : "https://api.bots.tf/rawtext", # STEAMID3-B
    "cheater" : "https://raw.githubusercontent.com/d3fc0n6/CheaterList/main/CheaterFriend/64ids", # STEAMID64
    "tacobot" : "https://raw.githubusercontent.com/d3fc0n6/TacobotList/master/64ids", # STEAMID64
    "pazer" : "https://raw.githubusercontent.com/d3fc0n6/PazerList/master/list.cfg", # STEAMID3-N
    "sleepy-rgl": "https://raw.githubusercontent.com/surepy/tf2db-sleepy-list/main/playerlist.rgl-gg.json" # STEAMID64
}

ID64_MAGIC_NUMBER = 76561197960265728

PAZER_REGEX = re.compile(r"\d+")

def parse_bot_list(list: str) -> str:
    list = list.splitlines()
    ids = []
    for i in list:
        ids.append(cvt(i, "STEAMID64"))
    return ids

def parse_rijin_list(list: str) -> str:
    list = list.splitlines()
    ids = []
    for i in list:
        ids.append(cvt(i, "STEAMID64"))
    return ids

def parse_pazer_list(list: str) -> str:
    list = list.splitlines()
    ids = []
    for i in list:
        ids.append(cvt(PAZER_REGEX.search(i).group(0), "STEAMID64"))
    return ids

def parse_tf2bd_list(list: str) -> str:
    list = json.loads(list)
    ids = []
    for p in list['players']:
        sid = p['steamid']
        ids.append(cvt(sid, "STEAMID64"))
    return ids