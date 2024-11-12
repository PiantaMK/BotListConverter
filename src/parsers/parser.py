import json
import re
import requests

from ..format import cvt

LISTS = {
    "bot" : "http://api.bots.tf/rawtext", # STEAMID3-B
    "cheater" : "https://raw.githubusercontent.com/d3fc0n6/CheaterList/main/CheaterFriend/64ids", # STEAMID64
    "tacobot" : "https://raw.githubusercontent.com/d3fc0n6/TacobotList/master/64ids", # STEAMID64
    "pazer" : "https://raw.githubusercontent.com/d3fc0n6/PazerList/master/list.cfg", # STEAMID3-N
    "sleepy-rgl": "https://raw.githubusercontent.com/surepy/tf2db-sleepy-list/main/playerlist.rgl-gg.json", # STEAMID64
    "sleepy-bot": "https://raw.githubusercontent.com/surepy/tf2db-sleepy-list/main/playerlist.sleepy-bots.merged.json" # STEAMID3-B
}

def get_latest_archived_url(url):
    data = requests.get(f"http://archive.org/wayback/available?url={url}").json()
    if data['archived_snapshots']:
        return data['archived_snapshots']['closest']['url']
    return None

def parse_bot_list(lst: str) -> str:
    return [cvt(i, "STEAMID64") for i in lst.splitlines()]

def parse_pazer_list(lst: str) -> str:
    return [cvt(re.compile(r"\d+").search(i).group(0), "STEAMID64") for i in lst.splitlines()]

def parse_tf2bd_list(lst: str) -> str:
    return [cvt(p['steamid'], "STEAMID64") for p in json.loads(lst)['players']]
