from utils.online import *

GET = "http://api.bots.tf/rawtext"

_pretty = "bots.tf - Bot"
def _main():
    lst = getlist(GET)
    return parse_generic(lst)