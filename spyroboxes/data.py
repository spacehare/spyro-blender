from dataclasses import dataclass, asdict
import json
from pathlib import Path
from .get_data import src_data, src_groups, src_verts
from mathutils import Vector


@dataclass(kw_only=True)
class SkySet:
    sky: str
    tetrahedron: str
    extras: str


@dataclass
class VertStuff:
    md5: str
    blender_object_name: str
    co_from: Vector
    co_to: Vector
    note: str
    ignore: bool

    @staticmethod
    def from_dict(d: dict) -> 'VertStuff':
        return VertStuff(
            md5=d['md5'],
            blender_object_name=d['blender_object_name'],
            co_from=Vector((
                int(d['from_x'] or 0),
                int(d['from_y'] or 0),
                int(d['from_z'] or 0),
            )),
            co_to=Vector((
                int(d['to_x'] or 0),
                int(d['to_y'] or 0),
                int(d['to_z'] or 0),
            )),
            note=d['note'],
            ignore=d['ignore'] == 'TRUE'
        )


PATH_ASSETS: Path = Path(__file__).parent / "assets"
if not PATH_ASSETS.exists():
    PATH_ASSETS.mkdir()
PATH_SKY_SETS: Path = PATH_ASSETS / "sky_sets.json"
sky_sets: list[SkySet] = []


def load_from_file():
    global sky_sets
    if not sky_sets:
        print('loading sky_sets for first time.')
        list_of_dicts = json.load(PATH_SKY_SETS.open("r"))
        sky_sets = [SkySet(**a) for a in list_of_dicts]
    return sky_sets


def save_sky_sets_to_file():
    json.dump([asdict(sky) for sky in sky_sets], PATH_SKY_SETS.open("w"))


sky_data: list = json.load(src_data.json_path.open())
group_data: list = json.load(src_groups.json_path.open())
nm_vert_data: list = json.load(src_verts.json_path.open())
'''non-manifold vert data (relevant to moving and prettifying verts) '''
nm_vertgroup_list: list[VertStuff] = [VertStuff.from_dict(d) for d in nm_vert_data]
