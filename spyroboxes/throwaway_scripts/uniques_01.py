import json
from pathlib import Path

outpath = Path('./out.json')
md5_list = []
data: list[dict] = json.load(Path('./data.json').open('r'))
md5_dict: dict[str, list] = {}

for item in data:
    what = {
        'FILENAME': item['FILENAME'],
        'NAME': item['NAME']
    }
    if item['TAG'] == 'S':
        if md5_dict.get(item['DATA_MD5']):
            md5_dict[item['DATA_MD5']].append(what)
        else:
            md5_dict[item['DATA_MD5']] = [what]

json.dump(md5_dict, outpath.open('w'))
