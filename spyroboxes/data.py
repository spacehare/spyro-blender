from bpy.types import Object
from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass(kw_only=True)
class SkySet:
    sky: str
    tetrahedron: str
    extras: str


PATH_TEMP_FILE = Path(Path(__file__).parent / "temp/temp.json")
sky_sets: list[SkySet] = []


def load_from_file():
    global sky_sets
    list_of_dicts = json.load(PATH_TEMP_FILE.open('r'))
    sky_sets = [SkySet(**a) for a in list_of_dicts]


def save_to_file():
    json.dump([asdict(sky) for sky in sky_sets], PATH_TEMP_FILE.open('w'))
