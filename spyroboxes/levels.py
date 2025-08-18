from pathlib import Path
from dataclasses import dataclass
import csv

CSV_FILE_PATH = Path(Path(__file__).parent / 'assets/levels.csv')


@dataclass(kw_only=True)
class LevelInfo:
    game: str
    id: str
    subarea: str
    tag: str
    lod: str


@dataclass(kw_only=True)
class Level:
    name: str
    # info: LevelInfo
    game: str
    id: str
    subarea: str = ''
    sphere: bool = False
    '''is the level's sky a sphere? (as opposed to a dome)'''
    sky: bool = True


levels: list[Level] = []
with open(CSV_FILE_PATH) as file:
    for row in csv.DictReader(file):
        levels.append(Level(
            name=row['NAME'], game=row['GAME'], id=row['ID'])
        )


def quake_ok_name(name: str):
    return name.replace(' ', '_').replace("'", '').lower()


# def validate(lvl: LevelInfo):
#     return all([
#         lvl.lod == "1",
#     ])


def info_from_stem(stem: str) -> LevelInfo:
    if len(stem) < 16:
        print("STEM TOO SHORT")

    lod = stem[3]  # i think this is the LOD? it should be 1
    game = stem[:2]
    id = stem[5:8]
    tag = stem[-5]
    subarea = ''

    if stem[9] != 'n':
        subarea = stem[9]

    return LevelInfo(
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
            if level.game == info.game and level.id == info.id:
                return level
