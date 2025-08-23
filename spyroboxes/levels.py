from pathlib import Path
from dataclasses import dataclass
import csv

CSV_FILE_PATH = Path(Path(__file__).parent / 'assets/data.csv')

tag_dict = {
    'S': 'SKY',
    'F': 'COLORS',
    'L': 'LOWPOLY',
    'M': 'LIGHTSHADE',
    'T': 'TEXTURES',
    'MW': 'LIGHTSHADE_WATER',
    'TW': 'TEXTURES_WATER'
}


@dataclass(kw_only=True)
class LevelStemInfo:
    '''this class is redundant now that i have all the data is in the big CSV'''
    game: str
    uid: str
    portal: str
    """
    the char at index 9 will be something other than '1' or 'n' if it is not a portal-preview, or a Spyro 3 subarea's data.  
    hub worlds have portals and need to preview skyboxes to those other realms.  
    """
    tag: str
    '''see the Suffixes class.'''
    lod: str
    '''level of detail.'''

    @staticmethod
    def from_stem(stem: str) -> 'LevelStemInfo':
        if len(stem) < 12:
            raise ValueError("%s TOO SHORT" % stem)
        elif stem.endswith('.obj'):
            raise ValueError('%s needs to be a stem, not a name' % stem)

        lod = stem[3]  # at least, i think this is the LOD? it should be 1
        game = stem[:2]
        uid = stem[5:8]
        tag = stem.split('.')[1]
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


@dataclass(kw_only=True)
class Level:
    filename: Path
    name: str
    game: int
    tag_human: str
    is_hub: bool = False
    is_first_occurrence: bool
    lod: int
    '''level of detail'''
    tag: str
    '''a suffix denoting what type of mesh this is. (a sky, a level's textures, a level's lighting, etc)'''
    uid: int
    '''unique level id'''
    portal: int
    '''hub portal, or Spyro 3 level subarea'''
    count: int
    '''how many times the text data inside of this OBJ is found in every OBJ file'''
    is_sphere: bool = False
    '''is the level's sky a sphere? (as opposed to a dome)'''
    manual: bool = False
    '''did i have to manually fix non-manifold issues like broken vertexes, etc?'''

    @staticmethod
    def from_dict(d: dict) -> 'Level':
        return Level(
            filename=Path(d['FILENAME']),
            name=d['NAME'],
            game=d['GAME'],
            tag=d['TAG'],
            lod=int(d['LOD'] or -1),
            uid=int(d['UID'] or -1),
            portal=int(d['PORTAL'] or -1),
            tag_human=d['TAG_HUMAN'],
            is_hub=d['IS_HUB'] == 'TRUE',
            is_sphere=d['IS_SPHERE'] == 'TRUE',
            manual=d['MANUAL'] == 'TRUE',
            is_first_occurrence=d['IS_FIRST_OCCURRENCE'] == 'TRUE',
            count=int(d['COUNT'])
        )


levels: dict[str, Level] = {}

with open(CSV_FILE_PATH) as file:
    for row in csv.DictReader(file):
        lvl = Level.from_dict(row)
        levels[row['FILENAME']] = lvl


def level_from_stem(stem: str) -> Level | None:
    return levels[stem + '.obj']


# def level_from_info(info: LevelStemInfo) -> Level | None:
#     for level in levels:
#         if level.game == int(info.game[1]) and level.uid == int(info.uid):
#             return level


# def level_from_stem(stem: str) -> Level | None:
#     '''take a path stem like `s2-1_040-n.S` and get name information from it by referring to the CSV'''

#     if 'sky' in stem:
#         return None
#     else:
#         info: LevelStemInfo = LevelStemInfo.from_stem(stem)

#         for level in levels:
#             if level.game == int(info.game[1]) and level.uid == int(info.uid):
#                 return level
