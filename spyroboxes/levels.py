from pathlib import Path
from dataclasses import dataclass
import json

# you need to convert the Google Docs CSV files to JSON first!
PATH_DATA = Path(Path(__file__).parent / 'assets/data.json')
PATH_GROUPS = Path(Path(__file__).parent / 'assets/groups.json')

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


@dataclass
class RabbitGroup:
    group_name: str
    file_name: str


@dataclass(kw_only=True)
class Level:
    filename: Path
    name: str
    'manually guessed name'
    name_override: str
    '''if the OBJ data is the same, prioritize the name of an earlier level'''
    game: int
    tag_human: str
    is_hub: bool = False
    is_first_occurrence: bool
    lod: int
    '''truly i don't know lol. i think it's related to cutscenes or something.'''
    tag: str
    '''a suffix denoting what type of mesh this is. (a sky, a level's textures, a level's lighting, etc)'''
    uid: int
    '''unique level id'''
    portal: int
    '''hub portal, or Spyro 3 level subarea'''
    is_sphere: bool = False
    '''is the level's sky a sphere? (as opposed to a dome)'''
    manual: bool = False
    '''do i have to manually fix non-manifold issues like broken vertexes, etc?'''
    data_md5: str
    '''unique [hashlib md5 hexdigest] for the OBJ's text data'''
    top_down_img_avg: str
    '''average hash of this sky rendered from above, sans tetrahedron. hash size = 32'''
    rabbit_similar: str
    rabbit_group: str

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
            data_md5=str(d['DATA_MD5']),
            name_override=str(d['NAME_OVERRIDE']),
            top_down_img_avg=str(d['TOP_DOWN_IMG_AVG']),
            rabbit_group=d['RABBIT_GROUP'],
            rabbit_similar=d['RABBIT_SIMILAR']
        )


levels: dict[str, Level] = {}
hashes: dict[str, Level] = {}
groups: list[RabbitGroup] = []

_json_data: list[dict] = json.load(PATH_DATA.open())
_json_groups: list[dict] = json.load(PATH_GROUPS.open())


for item in _json_data:
    level = Level.from_dict(item)
    levels[str(level.filename)] = level
    hashes[level.data_md5] = level

for group in _json_groups:
    groups.append(RabbitGroup(**group))

del _json_data
del _json_groups


# with open(DATA_FILE_PATH) as file:
#     for row in csv.DictReader(file):
#         lvl = Level.from_dict(row)
#         hashes[row['DATA_MD5']] = lvl
#         levels[row['FILENAME']] = lvl
