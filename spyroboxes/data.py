from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass(kw_only=True)
class SkySet:
    sky: str
    tetrahedron: str
    extras: str


PATH_ASSETS: Path = Path(__file__).parent / "assets"
if not PATH_ASSETS.exists():
    PATH_ASSETS.mkdir()
PATH_SKY_SETS: Path = PATH_ASSETS / "sky_sets.json"
sky_sets: list[SkySet] = []


def load_from_file():
    global sky_sets
    list_of_dicts = json.load(PATH_SKY_SETS.open("r"))
    sky_sets = [SkySet(**a) for a in list_of_dicts]
    return sky_sets


def save_to_file():
    json.dump([asdict(sky) for sky in sky_sets], PATH_SKY_SETS.open("w"))
