from pathlib import Path
from dataclasses import dataclass
import csv

CSV_FILE_PATH = Path(Path(__file__).parent / 'assets/levels.csv')


@dataclass(kw_only=True)
class LevelStemInfo:
    game: str
    id: str
    subarea: str
    tag: str
    lod: str


@dataclass(kw_only=True)
class Level:
    name: str
    # info: LevelInfo
    game: int
    id: int
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
            id=int(row['ID']),
            is_sphere=row['IS_SPHERE'] == 'TRUE',
            manual=row['MANUAL'] == 'TRUE',
        ))


def quake_ok_name(name: str):
    return name.replace(' ', '_').replace("'", '').lower()


# def validate(lvl: LevelInfo):
#     return all([
#         lvl.lod == "1",
#     ])


def info_from_stem(stem: str) -> LevelStemInfo:
    if len(stem) < 12:
        raise ValueError("%s TOO SHORT" % stem)
    elif stem.endswith('.obj'):
        raise ValueError('%s needs to be a stem, not a name' % stem)

    lod = stem[3]  # at least, i think this is the LOD? it should be 1
    game = stem[:2]
    id = stem[5:8]
    tag = stem[-1]
    subarea = ''

    if stem[9] != 'n':
        subarea = stem[9]

    return LevelStemInfo(
        game=game,
        id=id,
        lod=lod,
        tag=tag,
        subarea=subarea,
    )


def level_from_stem(stem: str) -> Level | None:
    '''take a path stem like `s2-1_040-n.S` and get name information from it by referring to the CSV'''

    if 'sky' in stem:
        return None
    else:
        info = info_from_stem(stem)

        for level in levels:
            if level.game == int(info.game[1]) and level.id == int(info.id):
                return level
