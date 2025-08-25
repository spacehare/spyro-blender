from . import render_sky
from . import data
from . import swv
from .levels import levels, hashes
from pathlib import Path
import bpy


def _add_all_skies(parent_folder: Path):
    '''import every unique sky'''
    results = []
    for key in hashes:
        if hashes[key].tag == 'S':
            result = add_single_object(parent_folder / hashes[key].filename)
            results.append(result)

    return results


def add_single_object(path_name: Path):
    '''import one instance'''
    file_name = path_name.name
    level = levels[file_name]
    new_name = level.name_override or level.data_md5
    obj = swv.import_spyro_obj(path_name)
    result = swv.organize_meshes(obj, new_name)
    return result


def batch_import_skies(parent_folder: Path):
    everything: list[tuple] = _add_all_skies(parent_folder)
    data.sky_sets = []
    for thing in everything:
        new_sky_set = data.SkySet(
            sky=thing[0].name,
            tetrahedron=thing[1].name,
            extras=thing[2].name if thing[2] else '',
        )
        data.sky_sets.append(new_sky_set)
    data.save_to_file()


def render_tests():
    assert (bpy.context.scene)
    all_objects = bpy.context.scene.objects
    skies = []
    sky_count = 0
    for obj in all_objects:
        bpy.data.objects[obj.name].hide_render = True
        bpy.data.objects[obj.name].hide_viewport = True

        # if 'Sky' in obj.name:
        #     print(sky_count, obj.name)
        #     sky_count += 1
        #     skies.append(obj)
