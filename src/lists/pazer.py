from utils.online import *

GET = "https://raw.githubusercontent.com/d3fc0n6/TacobotList/master/64ids"

_pretty = "d3fc0n6 - Pazer"
def _main():
    lst = getlist(GET)
    return parse_generic(lst)