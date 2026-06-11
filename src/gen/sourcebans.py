import sys, os, json
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
import cloudscraper
from bs4 import BeautifulSoup
import re
import html
import signal
import time
import argparse

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.format import SteamID

# sourcebans/++ banlist scraper
# supports both old and new sourcebans++ styles

def strip_text(element):
    return element.text.strip()

def get_rows_sb(player_table):
    rows = {}
    for row in player_table:
        header = row.find('td', width=re.compile(r'\d+%'), height='16')
        content = row.find('td', height='16', width=None)

        if len(content.contents) > 1:
            for child in content.contents:
                if child in ['\n', ' ']:
                    continue
                content = child
                break
        rows[strip_text(header)] = strip_text(content)

    return rows

def extract_data_sbpp(player_table):
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
        for item in player_table:
            if item.text.strip().startswith(column_name):
                value = item.text.split(column_name, 1)[1].strip()
                if key == 'id':
                    value = int(value)
                break
        data[key] = value
    
    return data

class SourceBansScraper:
    MODE_SOURCEBANS = 0
    MODE_SOURCEBANS_PP = 1

    def __init__(self, url, output_file):
        self.url = url
        self.output_file = output_file
        self.scraper = cloudscraper.create_scraper()
        self.mode = self.MODE_SOURCEBANS_PP
        self.pagecount = 0
        self.alldata = []

    def get_pg(self, page_index=1):
        if "{page}" in self.url:
            return self.url.format(page=page_index)
        if page_index == 1:
            return self.url
        parsed = urlparse(self.url)
        query = parse_qsl(parsed.query)
        query.append(('page', str(page_index)))
        new_query = urlencode(query)
        return urlunparse(parsed._replace(query=new_query))

    def detect_mode(self):
        detect_url = self.get_pg(1)
        print("Detecting scraper mode...")
        try:
            response = self.scraper.get(detect_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            if soup.find(class_='ban_list_detal') or soup.find(class_='table_hide'):
                print("Detected: SourceBans++")
                return self.MODE_SOURCEBANS_PP
            if soup.find('div', id='banlist') or soup.find('table', class_='listtable'):
                print("Detected: SourceBans")
                return self.MODE_SOURCEBANS
        except Exception as e:
            print(f"Error during auto-detection: {e}")
        print("Fallback: Defaulting to SourceBans++")
        return self.MODE_SOURCEBANS_PP

    def scrape_sb(self, pagenum=1):
        url = self.get_pg(pagenum)
        response = self.scraper.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        contentdiv = soup.find('div', id='content')
        if contentdiv.b.text == 'Fatal error':
            print(f"Serverside fatal error on page {pagenum} (not my fault)")
            return None

        selectpage = soup.find('select', onchange=lambda x: x and "changePage(this,'B','','');" in x)
        if selectpage:
            self.pagecount = len(selectpage.find_all('option'))
        else:
            self.pagecount = 1

        if pagenum > self.pagecount:
            print("Reached last page")
            return -1
        
        bantable = soup.find('div', id='banlist').table
        if not bantable:
            return None

        page_data = []
        for player in bantable.find_all('table', class_='listtable'):
            tables = get_rows_sb(player.find_all('tr', align='left'))
            steam2 = tables.get('Steam2') # only sourcebans
            steam3 = tables.get('Steam3 ID') # only sourcebans++

            steam_id = None
            if steam2 and steam2.startswith("STEAM_0"):
                steam_id = SteamID(steam2).id64
            elif steam3 and steam3.startswith("[U:1:"):
                steam_id = SteamID(steam3).id64

            if steam_id is None:
                continue
            data = {
                'nick': tables.get('Player'),
                'id': steam_id,
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

            if data.get('nick'):
                data['nick'] = html.unescape(data['nick'])

            keys_to_delete = [key for key, value in data.items() if value is None]
            for key in keys_to_delete:
                if key == 'nick':
                    continue
                if data[key] == None:
                    del data[key]

            page_data.append(data)
        return page_data

    def scrape_sbpp(self, pagenum=1):
        url = self.get_pg(pagenum)
        response = self.scraper.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        selectpage = soup.find('select', onchange=lambda x: x and "changePage(this,'B','','');" in x)
        if selectpage:
            self.pagecount = len(selectpage.find_all('option'))
        else:
            self.pagecount = 1

        if pagenum > self.pagecount:
            print("Reached last page")
            return -1
        
        bantable = soup.find_all('div', class_='table padding')[1].find_all('tr', class_='table_hide')
        if not bantable:
            return None
        
        page_data = []
        for player in bantable:
            data = extract_data_sbpp(player.find('ul', class_='ban_list_detal').find_all('li'))
            
            steam_id = None
            if data.get('id'):
                try:
                    steam_id = SteamID(data['id']).id64
                except ValueError:
                    pass
            
            if steam_id is None and data.get('id3'):
                try:
                    steam_id = SteamID(data['id3']).id64
                except ValueError:
                    pass
            
            if steam_id is None and data.get('id2'):
                try:
                    steam_id = SteamID(data['id2']).id64
                except ValueError:
                    pass

            if steam_id is None:
                continue

            data['id'] = steam_id
            data.pop('id2', None)
            data.pop('id3', None)

            if data.get('nick') is not None:
                nick = data['nick']
                nick = html.unescape(nick)
                if nick.lower() == 'no nickname present':
                    nick = None
                data['nick'] = nick

            keys_to_delete = [key for key, value in data.items() if value is None]
            for key in keys_to_delete:
                if key == 'nick':
                    continue
                if data[key] == None:
                    del data[key]
            page_data.append(data)
        return page_data

    def save(self):
        with open(self.output_file, "w") as f:
            json.dump(self.alldata, f, indent=4)
        print(f"Data saved to {self.output_file}")

    def signal_handler(self, sig_num, frame):
        print("\nCtrl+C detected. Saving data and exiting...")
        self.save()
        sys.exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.mode = self.detect_mode()

        current_page = 1
        while True:
            maxtries = 3
            print("Parsing page", current_page)
            pagedata = None

            while maxtries != 0:
                try:
                    if self.mode == self.MODE_SOURCEBANS:
                        pagedata = self.scrape_sb(current_page)
                    elif self.mode == self.MODE_SOURCEBANS_PP:
                        pagedata = self.scrape_sbpp(current_page)
                    else:
                        raise ValueError("Invalid MODE")
                    break # break out of maxtries
                except Exception as e:
                    print(f"Error parsing page {current_page}: {e}, retrying after 5 sec...")
                    time.sleep(5)
                    maxtries -= 1

            if maxtries == 0:
                print(f"Failed to fetch page {current_page} after 3 attempts. Stopping/saving.")
                break

            if pagedata == -1:
                break
            elif pagedata is None:
                current_page += 1
                continue
            elif pagedata:
                self.alldata.extend(pagedata)
            current_page += 1

        self.save()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SourceBans(++) Banlist Scraper")
    parser.add_argument("-u", "--url", required=True, help="Banlist URL")
    parser.add_argument("-o", "--output", required=True, help="Output JSON file path")
    args = parser.parse_args()

    scraper = SourceBansScraper(url=args.url, output_file=args.output)
    scraper.run()