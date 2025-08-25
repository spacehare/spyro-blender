from . import swv
from .levels import levels, hashes
from pathlib import Path


def add_all_skies(parent_folder: Path):
    '''import every unique sky'''
    for key in hashes:
        if hashes[key].tag == 'S':
            add_single_sky(parent_folder / hashes[key].filename)


def add_single_sky(path_name: Path):
    '''import one instance of one sky'''
    file_name = path_name.name
    level = levels[file_name]
    new_name = level.name_override or level.data_md5
    obj = swv.import_spyro_obj(path_name)
    swv.organize_meshes(obj, new_name)
