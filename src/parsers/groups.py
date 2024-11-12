import json
import os
import requests
import time

from bs4 import BeautifulSoup

CONFIG_PATH = 'groups.json'

def read_config():
    if not os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump({"settings": {}}, f)
    
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    
    settings = config.get('settings', {})
    group_file = settings.get('GROUP_FILE', 'groups.txt')
    last_launch = settings.get('LAST_LAUNCH', 0)
    
    changes_made = False
    
    if not os.path.isfile(group_file):
        new_group_file = input(f"{group_file} does not exist. Input the filename of your groups file (incl. the extension): ")
        settings['GROUP_FILE'] = new_group_file
        group_file = new_group_file
        changes_made = True

    return {
        'group_file': group_file,
        'last_launch': last_launch,
        'changes_made': changes_made,
        'config': config
    }

def getmembers(group, gids=False):
    if gids:
        group_url = f'https://steamcommunity.com/gid/{group}/memberslistxml/?xml=1'
    else:
        group_url = f'https://steamcommunity.com/groups/{group}/memberslistxml/?xml=1'
    
    while True:
        response = requests.get(group_url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'xml')
            members = soup.find_all('steamID64')
            member_ids = [int(member.text) for member in members]
            return member_ids
        
        elif response.status_code == 429:
            print(f"Rate limit hit for '{group}'. Waiting 30 seconds before retrying...")
            time.sleep(30)  # wait and retry if the rate limit is hit
        
        else:
            print(f"Failed to retrieve members for '{group}'. Status code: {response.status_code}")
            return []

def getgroups(cfgpath):
    members = {}
    try:
        with open(cfgpath, 'r') as file:
            group_names = [line.strip() for line in file.readlines() if not line.startswith("#")]
        
        total_groups = len([name for name in group_names if name])

        for i, group in enumerate(group_names, start=1):
            if group:
                print(f"Parsing group '{group}' ({i} out of {total_groups})")
                member_ids = getmembers(group)
                members[f"GROUP - {group}"] = member_ids
                if i % 5 == 0 and i != total_groups:  # wait 3 seconds after every 5 groups
                    time.sleep(3)

    except FileNotFoundError:
        print(f"{cfgpath} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return members

def check_cooldown(last_launch):
    now = time.time()
    diff = now - last_launch

    if diff < 30:
        cooldown = 20
        print(f"I was launched {int(diff)}s ago. Waiting {cooldown} seconds to not overload the Steam API...")
        time.sleep(cooldown)
    
    return now

def get():
    fig = read_config()
    current_time = check_cooldown(fig['last_launch'])

    fig['config']['settings']['LAST_LAUNCH'] = current_time
    if fig['changes_made'] or True:
        with open(CONFIG_PATH, 'w') as configfile:
            json.dump(fig['config'], configfile, indent=4)

    group_members_dict = getgroups(fig['group_file'])
    
    return group_members_dict