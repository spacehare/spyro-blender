import requests
import json
import csv
from pathlib import Path
from dataclasses import dataclass

PATH_PARENT = Path(Path(__file__).parent)
GID_DATA = 1622789080
GID_GROUPS = 1423109304
GID_VERTS = 2143495582


def create_url(gid: int):
    string = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vSK8neFMNBVxDJWFwB53Zqi-req0PGdBJQ9Gcc9VvEmR_VjG8pHYx0blDPo6PdHyplhESesuqui7Qz7/pub?gid={gid}&single=true&output=csv"
    return string


@dataclass
class Source:
    json_path: Path
    url: str


src_data: Source = Source(
    PATH_PARENT / 'assets/data.json',
    create_url(GID_DATA),
)
src_groups: Source = Source(
    PATH_PARENT / 'assets/groups.json',
    create_url(GID_GROUPS),
)
src_verts: Source = Source(
    PATH_PARENT / 'assets/verts.json',
    create_url(GID_VERTS),
)

for src in [src_data, src_groups, src_verts]:
    if src.json_path.exists():
        print('JSON file "%s" already exists; using it instead of fetching CSV via "requests".' % src.json_path)
        continue
    else:
        src.json_path.touch()
        result = requests.get(src.url)
        print('status_code:', result.status_code)

        reader = csv.DictReader(result.text.splitlines())
        json.dump(
            obj=[row for row in reader],
            fp=src.json_path.open('w'),
            indent='\t',
        )
