import cloudscraper
import re
import json
from bs4 import BeautifulSoup
import time

scraper = None
# rentamedic.org cheater list scraper

def get_pg(pgidx=1):
    return "https://rentamedic.org/cheaters/?page={page}".format(page=pgidx)

def cheaterinfo_req(ids):
    base = "https://rentamedic.org/api/cheaters/lookup?steamids="
    if isinstance(ids, list):
        if len(ids) > 100:
            raise ValueError("Too many IDs")
        ids = ','.join(map(str, ids))
    url = base + ids
    while True:
        response = scraper.get(url)
        if response.status_code == 429:
            print("Rate limit exceeded, waiting for 30 seconds")
            time.sleep(30)
        else:
            break
    return response.json()
 
def parse_pg(pagenum=1):
    retids = []
    url = get_pg(pagenum)
    response = scraper.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    pageinfo = soup.find('div', class_='pagination-status').text
    curpage, total = re.search(r'Page (\d+) of (\d+)', pageinfo).groups()

    if int(curpage) >= int(total):
        print("Reached last page")

    clist = soup.find('div', class_='cheater-list')
    if clist:
        table_body = clist.find('table').find('tbody')
        for row in table_body.find_all('tr'):
            id = int(row.find_all('td', class_='shrink')[1].a.attrs['href'].split('/cheaters/')[1])
            retids.append(id)
    else:
        print("No cheater-list div found")

    return retids

if __name__ == "__main__":
    scraper = cloudscraper.create_scraper()

    ids = []
    total_info = []
    r = [0] * 50
    
    i = 1
    while len(r) == 50:
        print("Parsing page", i)
        r = parse_pg(i)
        ids.extend(r)
        if len(ids) % 100 == 0 or len(r) < 50:
            print("Requesting info...")
            if len(ids) % 100 == 0:
                idsinfo = cheaterinfo_req(ids[-100:])
            else:
                idsinfo = cheaterinfo_req(ids[-len(r):])
            stuff = idsinfo['results'] # list of dicts (player info inside)
            total_info.extend(stuff)
        i += 1
    print(f"Total amount of profiles: {len(total_info)}")
    with open("rentamed.json", "w") as f:
        json.dump(total_info, f, indent=4)