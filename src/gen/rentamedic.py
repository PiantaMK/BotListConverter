import sys, os, json
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
import cloudscraper
from bs4 import BeautifulSoup
import re
import time
import argparse

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# rentamedic.org cheater list scraper

class RentAMedicScraper:
    def __init__(self, output_file):
        self.output_file = output_file
        self.scraper = cloudscraper.create_scraper()
        self.all_ids = []
        self.players_info = []

    def get_pg(self, page_index=1):
        return f"https://rentamedic.org/cheaters/?page={page_index}"

    def fetch_cheater_info(self, steam_ids):
        base_url = "https://rentamedic.org/api/cheaters/lookup?steamids="
        if len(steam_ids) > 100:
            raise ValueError("API lookup limit is 100 SteamIDs per request")
        
        ids_param = ','.join(map(str, steam_ids))
        url = base_url + ids_param
        
        while True:
            response = self.scraper.get(url)
            if response.status_code == 429:
                print("Rate limit exceeded, waiting for 30 seconds...")
                time.sleep(30)
            else:
                break
        return response.json()

    def parse_page(self, page_num=1):
        page_ids = []
        url = self.get_pg(page_num)
        response = self.scraper.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        pagination_status = soup.find('div', class_='pagination-status')
        if not pagination_status:
            print(f"Warning: No pagination status found on page {page_num}")
            return page_ids, True # treat as last page

        page_text = pagination_status.text
        match = re.search(r'Page (\d+) of (\d+)', page_text)
        if not match:
            return page_ids, True

        current_page, total_pages = match.groups()
        is_last_page = int(current_page) >= int(total_pages)

        cheater_list_div = soup.find('div', class_='cheater-list')
        if cheater_list_div:
            table_body = cheater_list_div.find('table').find('tbody')
            for row in table_body.find_all('tr'):
                anchor = row.find_all('td', class_='shrink')[1].a
                cheater_id = int(anchor.attrs['href'].split('/cheaters/')[1])
                page_ids.append(cheater_id)
        else:
            print("No cheater-list div found on page", page_num)

        return page_ids, is_last_page

    def save(self):
        with open(self.output_file, "w") as f:
            json.dump(self.players_info, f, indent=4)
        print(f"Data saved to {self.output_file}")

    def run(self):
        current_page = 1
        is_last = False

        # Step 1: Collect all cheater IDs from pagination
        while not is_last:
            print("Parsing page", current_page)
            page_ids, is_last = self.parse_page(current_page)
            self.all_ids.extend(page_ids)
            current_page += 1

        print(f"Collected {len(self.all_ids)} cheater IDs in total. Requesting API details...")

        # Step 2: Query player details in chunks of 100
        for chunk_start in range(0, len(self.all_ids), 100):
            chunk = self.all_ids[chunk_start : chunk_start + 100]
            print(f"Querying info for batch {chunk_start // 100 + 1}...")
            lookup_results = self.fetch_cheater_info(chunk)
            if 'results' in lookup_results:
                self.players_info.extend(lookup_results['results'])
            else:
                print(f"Warning: unexpected API response format for batch starting at {chunk_start}")

        print(f"Total profiles retrieved: {len(self.players_info)}")
        self.save()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RentAMedic Cheater List Scraper")
    parser.add_argument("-o", "--output", required=True, help="Output JSON file path")
    args = parser.parse_args()

    scraper = RentAMedicScraper(output_file=args.output)
    scraper.run()