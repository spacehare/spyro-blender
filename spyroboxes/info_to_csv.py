from .levels import info_from_stem, level_from_info
from pathlib import Path

PATH_FILENAMES = Path(Path(__file__).parent / './assets/filenames.txt')
PATH_OUTPUT = Path(Path(__file__).parent / './assets/output.csv')

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
            'STRIPPED',
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
        ]
    ) + '\n'

    for line in file:
        stripped = line.strip()
        level = None
        info = None
        if 'sky' in stripped:
            output += stripped + '\n'
        else:
            info = info_from_stem(stripped[:-4])
            if info:
                level = level_from_info(info)

            o_stripped = stripped
            o_name = str(level.name if level else '')
            o_game = str(info.game)
            o_uid = str(info.uid)
            o_is_sphere = str(level.is_sphere if level else '') if info.tag == 'S' else ''
            o_manual = str(level.manual if level else '')
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
                ]
            ) + '\n'

    PATH_OUTPUT.write_text(output, encoding='utf-8')
