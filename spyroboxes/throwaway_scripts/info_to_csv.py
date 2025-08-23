from spyroboxes.levels import info_from_stem, level_from_info
from pathlib import Path
import csv

PATH_FILENAMES = Path(Path(__file__).parent / './assets/filenames.txt')
PATH_RESULTS = Path(Path(__file__).parent / './assets/list_results.tsv')
PATH_OUTPUT = Path(Path(__file__).parent / './assets/output.csv')
DATA_RESULTS_DICTREADER = csv.DictReader(PATH_RESULTS.open(), delimiter='\t')
DATA_RESULTS_DICT = {}
for row in DATA_RESULTS_DICTREADER:
    DATA_RESULTS_DICT[row['FILENAME']] = row

tag_dict = {
    'S': 'SKY',
    'F': 'COLORS',
    'L': 'LOWPOLY',
    'M': 'LIGHTSHADE',
    'T': 'TEXTURES',
    'MW': 'LIGHTSHADE_WATER',
    'TW': 'TEXTURES_WATER'
}


def replace_tag(string: str) -> str:
    for key in tag_dict:
        if key == string:
            return tag_dict[key]


with open(PATH_FILENAMES, 'r', encoding='utf-8') as file:
    output = ''
    output += ','.join(
        [
            'FILENAME',
            'NAME',
            'GAME',
            'UID',
            'IS_SPHERE',
            'MANUAL',
            'LOD',
            'PORTAL',
            'TAG',
            'TAG_HUMAN',
            'IS_HUB',
            'COUNT',  # this is how many times the OBJ's text data repeats inside of the files
            'IS_FIRST_OCCURRENCE',  # first occurence of OBJ text data
        ]
    ) + '\n'

    for line in file:
        stripped = line.strip()
        level = None
        info = None

        o_count = str(DATA_RESULTS_DICT[stripped]['COUNT'])
        o_first = str(DATA_RESULTS_DICT[stripped]['FIRST_OCCURRENCE'])

        if 'sky' in stripped:
            output += ','.join(
                [
                    stripped,
                    '',
                    's3',
                    '',
                    '',
                    '',
                    '',
                    '',
                    'S',
                    'SKY',
                    '',
                    o_count,
                    o_first,
                ]
            ) + '\n'
        else:
            info = info_from_stem(stripped[:-4])
            if info:
                level = level_from_info(info)

            o_stripped = stripped
            o_name = str(level.name if level else '')
            o_game = str(info.game)
            o_uid = str(info.uid)
            o_is_sphere = str(level.is_sphere if level else '') if info.tag == 'S' else ''
            o_manual = str(level.manual if level else '') if info.tag == 'S' else ''
            o_lod = str(info.lod)
            o_portal = str(info.portal)
            o_tag = str(info.tag)
            o_tag_replaced = str(replace_tag(o_tag))
            o_is_hub = str(level.is_hub if level else '')

            output += ','.join(
                [
                    o_stripped,
                    o_name,
                    o_game,
                    o_uid,
                    o_is_sphere,
                    o_manual,
                    o_lod,
                    o_portal,
                    o_tag,
                    o_tag_replaced,
                    o_is_hub,
                    o_count,
                    o_first,
                ]
            ) + '\n'

    PATH_OUTPUT.write_text(output, encoding='utf-8')
