import json
import requests

from src.utils.format import SteamID

def get_latest_archived_url(url):
    data = requests.get(f"http://archive.org/wayback/available?url={url}").json()
    if data['archived_snapshots']:
        return data['archived_snapshots']['closest']['url']
    return None

def getlist(url):
    response = requests.get(url)
    if response.status_code == 200:
        return str(response.text)
    else:
        response = requests.get(get_latest_archived_url(url))
        if response.status_code == 200:
            return str(response.text)
        else:
            return None
        
def parse_generic(lst):
    return [SteamID(i).id64 for i in lst.splitlines()]

def parse_tf2bd(lst):
    return [SteamID(p['steamid']).id64 for p in json.loads(lst)['players']]