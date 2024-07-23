from dataclasses import dataclass
import csv


@dataclass
class Level:
    name: str
    game: int
    level_id: int
    sphere: bool = False
    '''is the level's sky a sphere?'''
    sky: bool = True


def quake_ok_name(name: str):
    return name.replace(' ', '_').replace("'", '').lower()


levels: list[Level] = []

with open('levels.csv') as file:
    for row in csv.DictReader(file):
        levels.append(Level(row['NAME'], int(row['GAME']), int(row['ID'])))
