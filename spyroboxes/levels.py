from pathlib import Path
from dataclasses import dataclass
import csv

CSV_FILE_PATH = Path(Path(__file__).parent / 'assets/levels.csv')


@dataclass(kw_only=True)
class LevelStemInfo:
    game: str
    uid: str
    '''level id'''
    portal: str
    """
    the char at index 9 will be something other than '1' or 'n' if it is not a portal-preview.  
    hub worlds have portals and need to preview skyboxes to those other realms.  
    we can ignore these, they are redundant.
    """
    tag: str
    '''see the Suffixes class.'''
    lod: str
    '''level of detail.'''


@dataclass(kw_only=True)
class Level:
    name: str
    # info: LevelInfo
    game: int
    uid: int
    '''level id'''
    # subarea: str = ''
    is_sphere: bool = False
    '''is the level's sky a sphere? (as opposed to a dome)'''
    manual: bool = False
    '''did i have to manually fix broken vertexes, etc?'''


levels: list[Level] = []
with open(CSV_FILE_PATH) as file:
    for row in csv.DictReader(file):
        levels.append(Level(
            name=row['NAME'],
            game=int(row['GAME']),
            uid=int(row['ID']),
            is_sphere=row['IS_SPHERE'] == 'TRUE',
            manual=row['MANUAL'] == 'TRUE',
        ))


def quake_ok_name(name: str):
    return name.replace(' ', '_').replace("'", '').lower()


def info_from_stem(stem: str) -> LevelStemInfo:
    if len(stem) < 12:
        raise ValueError("%s TOO SHORT" % stem)
    elif stem.endswith('.obj'):
        raise ValueError('%s needs to be a stem, not a name' % stem)

    lod = stem[3]  # at least, i think this is the LOD? it should be 1
    game = stem[:2]
    uid = stem[5:8]
    tag = stem[-1]
    portal = ''

    if stem[9] != 'n':
        portal = stem[9]

    return LevelStemInfo(
        game=game,
        uid=uid,
        lod=lod,
        tag=tag,
        portal=portal,
    )


def level_from_stem(stem: str) -> Level | None:
    '''take a path stem like `s2-1_040-n.S` and get name information from it by referring to the CSV'''

    if 'sky' in stem:
        return None
    else:
        info = info_from_stem(stem)

        for level in levels:
            if level.game == int(info.game[1]) and level.uid == int(info.uid):
                return level
