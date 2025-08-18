from pathlib import Path
from dataclasses import dataclass
import csv
import re

RE_VALID = re.compile(r"s\d-(1)_(\d{3})-n.(S)(?!\.obj)?")


@dataclass
class Level:
    name: str
    game: int
    id: int
    subarea: int = 0
    sphere: bool = False
    '''is the level's sky a sphere?'''
    sky: bool = True


levels: list[Level] = []
with open('assets/levels.csv') as file:
    for row in csv.DictReader(file):
        levels.append(Level(row['NAME'], int(row['GAME']), int(row['ID'])))


def quake_ok_name(name: str):
    return name.replace(' ', '_').replace("'", '').lower()


def validate(string: str):
    return RE_VALID.match(string)


def info_from_stem(stem: str):
    m = RE_VALID.match(stem)
    if m:
        g = m.groups()
        game = int(g[0])
        id = int(g[1])
        subarea = int(g[3]) if g[3] else 0
        tag = g[4]

        return game, id, subarea, tag


def level_from_path_str(name: str | Path):
    '''take a path stem like `s2-1_040-n.S` and get name information from it by referring to the CSV'''
    if isinstance(name, Path):
        name = name.stem

    if 'sky' in name:
        pass
    else:
        game, id, _ = info_from_stem(name)

        for level in levels:
            if level.game == game and level.id == id:
                return level
