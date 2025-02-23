from src.utils.online import *

GET = "https://raw.githubusercontent.com/surepy/tf2db-sleepy-list/main/playerlist.rgl-gg.json"

_pretty = "Sleepy List - RGL"
def _main():
    lst = getlist(GET)
    return parse_tf2bd(lst)