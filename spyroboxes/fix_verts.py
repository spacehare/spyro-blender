import bpy
from . import swv
from .data import nm_vertgroup_list
from mathutils import Vector

# the values in the raw OBJ data are integers


def to_imported_scale(value: float | int) -> float:
    return value * swv.SCALE


def from_imported_scale(value: float) -> float:
    return value / swv.SCALE


def move_verts(blender_object_name: str, move: bool):
    print('adjusting "%s"' % blender_object_name)
    obj = bpy.data.objects.get(blender_object_name)
    if not obj:
        print("no object found")
        return
    md5_string = blender_object_name.split('_')[0]
    matching_vertgroups = [vg for vg in nm_vertgroup_list if vg.md5 == md5_string]
    match_found = False

    for vertgroup in matching_vertgroups:
        if vertgroup.ignore:
            continue
        print('\tmatching vertgroup found')

        for vertex in obj.data.vertices:
            converted: Vector = Vector((
                from_imported_scale(vertex.co.x),
                from_imported_scale(vertex.co.y),
                from_imported_scale(vertex.co.z)
            ))

            check = all([
                vertgroup.co_from[0] == round(converted.x),
                vertgroup.co_from[1] == round(converted.y),
                vertgroup.co_from[2] == round(converted.z),
            ])

            if check:
                match_found = True

                print('\t-> match:', vertgroup.co_from, converted)
                if move:
                    new_vec = Vector((
                        to_imported_scale(vertgroup.co_to[0]),
                        to_imported_scale(vertgroup.co_to[1]),
                        to_imported_scale(vertgroup.co_to[2]),
                    ))
                    print('new_vec', new_vec)
                    vertex.co = new_vec

    if match_found and move:
        obj.hide_viewport = False
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.0005)
        bpy.ops.mesh.select_all(action='DESELECT')

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        obj.hide_viewport = True
