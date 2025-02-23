# note: the main script chdirs to the root directory
from src.utils.format import remove_duplicates
import json

_name = 'Example custom ID list', # display/category name
_ext = '.json' # file extension, there will be no extension if _ext is not present
def _main():
    dbpath = r'ugcgaming-sbpp.json' # change this to the path of your database json

    with open(dbpath, 'r') as f:
        db = json.load(f)
    
    ids = [item.get('id', -1) for item in db] # get all IDs
    ids = [i for i in ids if i != -1] # remove invalid IDs
    ids = remove_duplicates(ids) # remove duplicates

    return {_name: ids} # named format (dict)

    # you can do this to return in a list format
    # return ids