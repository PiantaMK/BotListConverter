from utils.online import *

GET = "https://raw.githubusercontent.com/surepy/tf2db-sleepy-list/main/playerlist.sleepy-bots.merged.json"

_pretty = "Sleepy List - Bots"
def _main():
    lst = getlist(GET)
    return parse_tf2bd(lst)