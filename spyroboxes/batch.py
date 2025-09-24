from . import render_sky
from . import data
from . import swv
from . import setup
from . import quake
from . import fix_verts
from .levels import levels, hashes, groups
from pathlib import Path
import bpy
from bpy.types import Object


def _add_all_skies(parent_folder: Path):
    '''import every unique sky, based on the OBJ's md5 hash'''
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
    objects = swv.organize_meshes(obj, new_name, level.merge_exclusions)
    return objects


def get_groups_whitelist() -> list[str]:
    return [g.file_name for g in groups]


def batch_import_skies(objs_parent: Path, whitelist: list = []):
    everything: list[tuple] = []
    if whitelist:
        for key in levels:
            if str(levels[key].filename) in whitelist:
                everything.append(add_single_object(objs_parent / levels[key].filename))
    else:
        everything = _add_all_skies(objs_parent)
    data.sky_sets = []
    for thing in everything:
        new_sky_set = data.SkySet(
            sky=thing[0].name,
            tetrahedron=thing[1].name,
            extras=thing[2].name if thing[2] else '',
        )
        data.sky_sets.append(new_sky_set)
    data.save_sky_sets_to_file()


def render_single_top(*, output_parent: Path, sky_set: data.SkySet, res_xy: int, render_tetra: bool = True):
    obj_sky = bpy.data.objects[sky_set.sky]
    obj_tetra = bpy.data.objects[sky_set.tetrahedron] if render_tetra else None
    obj_extras = bpy.data.objects.get(sky_set.extras)

    toggle_vis_in_render(obj_sky, obj_tetra, obj_extras, False)

    filename = (output_parent / sky_set.sky.split('_')[1]).with_suffix('.png')
    print('rendering filename: %s' % filename)
    render_sky.render_top_preview(output_file_path=filename, res_xy=res_xy)

    toggle_vis_in_render(obj_sky, obj_tetra, obj_extras, True)


def render_tops_tests(output_parent: Path, res_xy: int, include_tetra: bool = True):
    print("==== render_tests has started ====")

    assert (bpy.context.scene)
    all_objects = bpy.context.scene.objects
    for obj in all_objects:
        if obj is not bpy.context.scene.camera:
            bpy.data.objects[obj.name].hide_render = True
            bpy.data.objects[obj.name].hide_viewport = True

    for sky_set in data.sky_sets:
        render_single_top(output_parent=output_parent, sky_set=sky_set, res_xy=res_xy, render_tetra=include_tetra)

    print("==== render_tests has finished! ====")


def toggle_vis_in_render(sky: Object, tetra: Object | None, extras: Object | None, state: bool):
    sky.hide_render = state
    if tetra:
        tetra.hide_render = state
    if extras:
        extras.hide_render = state


def render_all_skyboxes(output_parent: Path, res_xy: int, *, list_from: int = 0, list_to: int = 999, full_size_down: bool = True):
    print("==== render_all_skyboxes has started ====")

    camera = setup.setup_camera()

    all_objects = bpy.context.scene.objects
    for obj in all_objects:
        if obj is not bpy.context.scene.camera:
            bpy.data.objects[obj.name].hide_render = True
            bpy.data.objects[obj.name].hide_viewport = True

    for sky_set in data.sky_sets[list_from:list_to]:
        obj_sky = bpy.data.objects[sky_set.sky]
        obj_tetra = bpy.data.objects[sky_set.tetrahedron]
        obj_extras = bpy.data.objects.get(sky_set.extras)

        toggle_vis_in_render(obj_sky, obj_tetra, obj_extras, False)
        split = obj_sky.name.split('_')
        new_name: str = quake.quake_ok_name(split[1])
        data_hash = split[0]
        is_sphere: bool = hashes[data_hash].is_sphere
        render_sky.render_skybox(output_parent / new_name, camera, res_xy, False if full_size_down else is_sphere)
        toggle_vis_in_render(obj_sky, obj_tetra, obj_extras, True)

    print("==== render_all_skyboxes has finished ====")


def fix_all_verts():
    for sky_set in data.sky_sets:
        print('fixing ->', sky_set.sky)
        fix_verts.move_verts(sky_set.sky, True)
