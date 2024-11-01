import json
import requests
import time
import os
from bs4 import BeautifulSoup

CONFIG_FILE = 'groups.json'
PROFILE_URL_BASE = 'https://steamcommunity.com/profiles/'

#def __dbg_dict_len(d):
#    for key, value in d.items():
#        count = len(value) if hasattr(value, '__len__') else 0
#        print(f"{key} has {count} ids")

def read_config():
    if not os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"settings": {}}, f)
    
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    
    settings = config.get('settings', {})
    group_file = settings.get('GROUP_FILE', 'groups.txt')
    last_launch = settings.get('LAST_LAUNCH', 0)
    
    changes_made = False
    
    if not os.path.isfile(group_file):
        new_group_file = input(f"{group_file} does not exist. Please provide the filename of your groups file (incl. the extension): ")
        settings['GROUP_FILE'] = new_group_file
        group_file = new_group_file
        changes_made = True

    return group_file, last_launch, changes_made, config

def get_group_members(group_name, gids=False):
    if gids:
        group_url = f'https://steamcommunity.com/gid/{group_name}/memberslistxml/?xml=1'
    else:
        group_url = f'https://steamcommunity.com/groups/{group_name}/memberslistxml/?xml=1'
    
    while True:
        response = requests.get(group_url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'xml')
            members = soup.find_all('steamID64')
            member_ids = [int(member.text) for member in members]
            return member_ids
        
        elif response.status_code == 429:
            print(f"Rate limit hit for '{group_name}'. Waiting 30 seconds before retrying...")
            time.sleep(30)  # wait and retry if the rate limit is hit
        
        else:
            print(f"Failed to retrieve members for '{group_name}'. HTTP Status Code: {response.status_code}")
            return []

def process_group_file(file_path):
    group_members = {}
    try:
        with open(file_path, 'r') as file:
            group_names = [line.strip() for line in file.readlines() if not line.startswith("#")]
        
        total_groups = len([name for name in group_names if name])

        for i, group_name in enumerate(group_names, start=1):
            if group_name:
                print(f"Parsing group '{group_name}' ({i} out of {total_groups})")
                member_ids = get_group_members(group_name)
                group_members[f"GROUP - {group_name}"] = member_ids
                if i % 5 == 0 and i != total_groups:  # wait 3 seconds after every 5 groups
                    time.sleep(3)

    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return group_members

def check_cooldown(last_launch):
    current_time = time.time()
    time_since_last_launch = current_time - last_launch

    if time_since_last_launch < 30:
        cooldown_time = 20
        print(f"I was launched {int(time_since_last_launch)}s ago. Waiting {cooldown_time} seconds to not overload the Steam API...")
        time.sleep(cooldown_time)
    
    return current_time

def get():
    group_file, last_launch, changes_made, config = read_config()
    current_time = check_cooldown(last_launch)

    config['settings']['LAST_LAUNCH'] = current_time
    if changes_made or True:
        with open(CONFIG_FILE, 'w') as configfile:
            json.dump(config, configfile, indent=4)

    group_members_dict = process_group_file(group_file)

    #print(__dbg_dict_len(group_members_dict))
    
    return group_members_dict
