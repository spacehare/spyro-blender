from . import render_sky
from . import data
from . import swv
from .levels import levels, hashes
from pathlib import Path
import bpy
from bpy.types import Object


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
    new_name = f"{level.data_md5}_{level.name_override or 'UNNAMED'}"
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


def render_single(*, output_parent: Path, sky_set: data.SkySet, res_xy: int, render_tetra: bool = True):
    obj_sky = bpy.data.objects[sky_set.sky]
    obj_tetra = bpy.data.objects[sky_set.tetrahedron] if render_tetra else None
    obj_extras = bpy.data.objects.get(sky_set.extras)

    toggle_vis_in_render(obj_sky, obj_tetra, obj_extras, False)

    filename = output_parent / (sky_set.sky + '.png')
    render_sky.render_top_preview(output_file_path=filename, res_xy=res_xy)

    toggle_vis_in_render(obj_sky, obj_tetra, obj_extras, True)


def render_tests(output_parent: Path, res_xy: int, include_tetra: bool = True):
    print("==== render_tests has started ====")

    assert (bpy.context.scene)
    all_objects = bpy.context.scene.objects
    for obj in all_objects:
        if obj is not bpy.context.scene.camera:
            bpy.data.objects[obj.name].hide_render = True
            bpy.data.objects[obj.name].hide_viewport = True

    sky_sets = data.load_from_file()
    for sky_set in sky_sets:
        render_single(output_parent=output_parent, sky_set=sky_set, res_xy=res_xy, render_tetra=include_tetra)

    print("==== render_tests has finished! ====")


def toggle_vis_in_render(sky: Object, tetra: Object | None, extras: Object | None, state: bool):
    sky.hide_render = state
    if tetra:
        tetra.hide_render = state
    if extras:
        extras.hide_render = state
