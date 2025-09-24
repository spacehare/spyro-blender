import bpy
from . import swv
from .data import nm_vertgroup_list
from mathutils import Vector

# the values in the data are integers


def to_imported_scale(value: float | int) -> float:
    return value * swv.SCALE


def from_imported_scale(value: float) -> int:
    return int(value / swv.SCALE)


def adjust(blender_object_name: str, move: bool = False):
    print('adjusting "%s"' % blender_object_name)
    obj = bpy.data.objects.get(blender_object_name)
    md5_string = blender_object_name.split('_')[0]
    matching_vertgroups = [vg for vg in nm_vertgroup_list if vg.md5 == md5_string]

    for vertgroup in matching_vertgroups:
        if vertgroup.ignore:
            continue
        print('\tmatching vertgroup found')

        for vertex in obj.data.vertices:
            int_vec: Vector = Vector((
                from_imported_scale(vertex.co.x),
                from_imported_scale(vertex.co.y),
                from_imported_scale(vertex.co.z)
            ))

            print('try', vertgroup.co_from, vertex.co)
            if vertgroup.co_from == int_vec:
                print('\t\tmatch:', vertgroup.co_from, int_vec)
                if move:
                    vertex.co = Vector((
                        to_imported_scale(vertgroup.co_from.x),
                        to_imported_scale(vertgroup.co_from.y),
                        to_imported_scale(vertgroup.co_from.z),
                    ))
