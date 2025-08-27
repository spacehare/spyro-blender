import requests
import json
import csv
from pathlib import Path
from dataclasses import dataclass

PATH_PARENT = Path(Path(__file__).parent)
URL_SHEET_DATA: str = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSK8neFMNBVxDJWFwB53Zqi-req0PGdBJQ9Gcc9VvEmR_VjG8pHYx0blDPo6PdHyplhESesuqui7Qz7/pub?gid=1622789080&single=true&output=csv"
URL_SHEET_GROUPS: str = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSK8neFMNBVxDJWFwB53Zqi-req0PGdBJQ9Gcc9VvEmR_VjG8pHYx0blDPo6PdHyplhESesuqui7Qz7/pub?gid=1423109304&single=true&output=csv"


@dataclass
class Source:
    json_path: Path
    csv_path: Path
    url: str


src_data: Source = Source(
    PATH_PARENT / 'assets/data.json',
    PATH_PARENT / 'temp/data.csv',
    URL_SHEET_DATA,
)
src_groups: Source = Source(
    PATH_PARENT / 'assets/groups.json',
    PATH_PARENT / 'temp/groups.csv',
    URL_SHEET_GROUPS,
)

for src in [src_data, src_groups]:
    text = ''

    src.csv_path.touch()
    src.json_path.touch()

    if src.csv_path.exists():
        print('CSV file already exists; using it instead of fetching via "requests".')
        text = src.csv_path.read_text()
    else:
        result = requests.get(src.url)
        text = result.text
        print('status_code:', result.status_code)
        src.csv_path.write_text(text)

    with open(src.json_path, 'w') as file:
        reader = csv.DictReader(text.splitlines())
        list_of_dicts: list[dict] = []

        for row in reader:
            list_of_dicts.append(row)

        json.dump(list_of_dicts, file, indent='\t')
