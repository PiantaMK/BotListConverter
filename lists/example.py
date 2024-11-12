from src.format import remove_duplicates
import json

__ATTR__ = {
    'name': 'Example custom ID list',
}

def __call__():
    dbpath = r'ugcgaming-sbpp.json'

    with open(dbpath, 'r') as f:
        db = json.load(f)
    ids = [item.get('id', -1) for item in db]
    ids = [i for i in ids if i != -1]
    ids = remove_duplicates(ids)
    return {__ATTR__['name']: ids}