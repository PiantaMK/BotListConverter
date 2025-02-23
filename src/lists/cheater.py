from src.utils.online import *

GET = "https://raw.githubusercontent.com/d3fc0n6/CheaterList/main/CheaterFriend/64ids"

_pretty = "d3fc0n6 - Cheater"
def _main():
    lst = getlist(GET)
    return parse_generic(lst)