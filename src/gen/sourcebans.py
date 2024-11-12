import sys, os, json
import cloudscraper
from bs4 import BeautifulSoup
import re
import html
import signal
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from format import cvt

#? sourcebans/++ banlist scraper
#? supports both old and new sourcebans++ styles

pagecount = 0
output_file = "sourcebans-output.json"

SB = 0   # sourcebans page
SBPP = 1 # sourcebans++ page

#? example site
SITE = "https://bans.blackwonder.tf/index.php?p=banlist&page={page}"
MODE = SBPP

def get_pg(pgidx=1):
    return SITE.format(page=pgidx)

def _(s):
    return s.text.strip()

def get_cols_sb(playertbl):
    tables = {}
    for col in playertbl:
        header = col.find('td', width=re.compile(r'\d+%'), height='16')
        content = col.find('td', height='16', width=None)

        if len(content.contents) > 1:
            for c in content.contents:
                if c in ['\n', ' ']:
                    continue
                content = c
                break
        tables[_(header)] = _(content)

    return tables

def parse_pg_sb(pagenum=1):
    global pagecount
    url = get_pg(pagenum)
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    contentdiv = soup.find('div', id='content')
    if contentdiv.b.text == 'Fatal error':
        print(f"Serverside fatal error on page {pagenum} (not my fault)")
        return None

    selectpage = soup.find('select', onchange=lambda x: x and "changePage(this,'B','','');" in x)
    pagecount = len(selectpage.find_all('option'))

    if pagenum > pagecount:
        print("Reached last page")
        return -1
    
    bantable = soup.find('div', id='banlist').table
    if not bantable:
        return None

    alldata = []
    for player in bantable.find_all('table', class_='listtable'):
        tables = get_cols_sb(player.find_all('tr', align='left'))
        data = {
            'nick': tables.get('Player'),
            '_id2-sb': tables.get('Steam2'),
            '_id3-sbpp': tables.get('Steam3 ID'),
            'bandate': tables.get('Invoked on'),
            'banlength': tables.get('Ban length') or tables.get('Banlength'),
            'expires': tables.get('Expires on'),
            'reason': tables.get('Reason'),
            'admin': tables.get('Banned by Admin'),
            'banfrom': tables.get('Banned from'),

            # optional
            'unbanreason': tables.get('Unban reason'),
            'unbannedby': tables.get('Unbanned by Admin'),
        }

        # this column is only in sourcebans
        if data['_id2-sb'] and data['_id2-sb'].startswith("STEAM_0"):
            data['id'] = cvt(data['_id2-sb'], "STEAMID64")
            del data['_id2-sb']

        # this column is only in sourcebans++
        elif data['_id3-sbpp'] and data['_id3-sbpp'].startswith("[U:1:"):
            data['id'] = cvt(data['_id3-sbpp'], "STEAMID64")
            del data['_id3-sbpp']
        else:
            data['id'] = None
            continue

        data['nick'] == html.unescape(data['nick'])

        keys_to_delete = [k for k, v in data.items() if v is None]
        for k in keys_to_delete:
            if k == 'nick':
                continue
            if data[k] == None:
                del data[k]

        alldata.append(data)
    return alldata

def extract_data_sbpp(playertbl):
    column_map = {
        'nick': "Player\n",
        'id2': "Steam ID\n",
        'id3': "Steam3 ID\n",
        'id': "Steam Community\n",
        'bandate': "Invoked on\n",
        'banlength': "Ban length\n",
        'expires': "Expires on\n",
        'reason': "Reason\n",
        'admin': "Banned by Admin\n",

        # optional
        'unbanreason': "Unban reason\n",
        'unbannedby': "Unbanned by Admin\n",
    }
    
    data = {}
    for key, column_name in column_map.items():
        value = None
        for item in playertbl:
            if item.text.strip().startswith(column_name):
                value = item.text.split(column_name, 1)[1].strip()
                if key == 'id':
                    value = int(value)
                break
        data[key] = value
    
    return data

def parse_pg_sbpp(pagenum=1):
    url = get_pg(pagenum)
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    selectpage = soup.find('select', onchange=lambda x: x and "changePage(this,'B','','');" in x)
    pagecount = len(selectpage.find_all('option'))

    if pagenum > pagecount:
        print("Reached last page")
        return -1
    
    bantable = soup.find_all('div', class_='table padding')[1].find_all('tr', class_='table_hide')
    if not bantable:
        return None
    
    alldata = []
    for player in bantable:
        data = extract_data_sbpp(player.find('ul', class_='ban_list_detal').find_all('li'))
        if data.get('nick') is not None:
            nick = data['nick']
            nick = html.unescape(nick)
            if nick.lower() == 'no nickname present':
                nick = None

        keys_to_delete = [k for k, v in data.items() if v is None]
        for k in keys_to_delete:
            if k == 'nick':
                continue
            if data[k] == None:
                del data[k]
        alldata.append(data)
    return alldata

def save(output_file, alldata):
    with open(output_file, "w") as f:
        json.dump(alldata, f, indent=4)
    print(f"Data saved to {output_file}")

def signal_handler(sig, frame):
    print("\nCtrl+C detected. Saving data and exiting...")
    save(output_file, alldata)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    alldata = []
    i = 1
    while True:
        maxtries = 3
        print("Parsing page", i)

        while maxtries != 0:
            try:
                if MODE == SB:
                    pagedata = parse_pg_sb(i)
                elif MODE == SBPP:
                    pagedata = parse_pg_sbpp(i)
                else:
                    raise ValueError("Invalid MODE")
                break # break out of maxtries
            except Exception as e:
                print(f"Error parsing page {i}: {e}, retrying after 5 sec...")
                time.sleep(5)
                maxtries -= 1

        if pagedata == -1:
            break
        elif pagedata is None:
            i += 1
            continue
        elif pagedata:
            for plr in pagedata:
                alldata.append(plr)
        i += 1

    save(output_file, alldata)