import json
from pathlib import Path
import csv

outpath = Path('./matches.csv')
outpath.touch()
data: list[dict] = json.load(Path('./data.json').open('r'))
md5_dict: dict[str, list] = json.load(Path('./md5_00.json').open('r'))


def to_dict() -> dict:
    out = {}
    for key in md5_dict:
        tags = []
        filenames = []
        for i_dict in md5_dict[key]:
            filename = i_dict['FILENAME']
            filenames.append(filename)
            tag = filename.split('.')[1]
            tags.append(tag)

        tags_same = len(set(tags)) == 1
        assert (tags_same)
        out[key] = {"TAG": tags[0], "FILENAMES": filenames}

    return out


with open(outpath, 'w', newline='') as csvfile:
    fieldnames = ['MD5', 'TAG', 'FILENAMES']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    d = to_dict()
    for key in d:
        writer.writerow({
            "MD5": key,
            "TAG": d[key]['TAG'],
            "FILENAMES": d[key]['FILENAMES']
        })
