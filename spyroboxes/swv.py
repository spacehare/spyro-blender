'''
import the OBJ from SpyroWorldViewr into blender as a mesh.

https://en.wikipedia.org/wiki/Wavefront_.obj_file
'''

import bpy
from bpy.types import Object, Mesh, Attribute, AttributeGroupMesh
from pathlib import Path
from typing import NamedTuple
from enum import StrEnum
from dataclasses import dataclass
from . import levels

SCALE = 1/32


class Suffixes(StrEnum):
    SKY = 'S'
    F = 'F'
    L = 'L'
    M = 'M'
    T = 'T'
    MW = 'MW'
    TW = 'TW'


class Tags(StrEnum):
    VERT = 'v'  # int int int -> (int, int, int)
    UVW = 'vt'  # 0.0 - 1.0 -> float
    GROUP = 'g'  # str
    FACE = 'f'  # int / int -> (int, int)


class Vert(NamedTuple):
    x: int
    y: int
    z: int


class UVW(NamedTuple):
    u: float
    v: float
    w: float


@dataclass
class FaceIndexes:
    v_idx: int
    vt_idx: int

    @staticmethod
    def from_str(string: str):
        split = string.split('/')
        return FaceIndexes(*[int(s) - 1 for s in split])  # indexes in the OBJ file start at 1


@dataclass
class Face:
    a: FaceIndexes
    b: FaceIndexes
    c: FaceIndexes

    @staticmethod
    def from_str(string: str):
        split = string.split(' ')
        return Face(*[FaceIndexes.from_str(s) for s in split[1:]])


class OBJ:
    def __init__(self, name: str = '', uvws: list[UVW] = [], verts: list[Vert] = [], faces: list[Face] = []):
        self.name = name
        self.uvws = uvws or []
        self.verts = verts or []
        self.faces = faces or []


def get_uvw_from_vert_idx(groups: list[OBJ], all_uvws: list[UVW], idx: int):
    for group in groups:
        for face in group.faces:
            for point in [face.a, face.b, face.c]:
                if idx == point.v_idx:
                    return all_uvws[point.vt_idx]


def import_spyro_obj(path: Path):
    '''
    SpyroWorldViewer OBJ line order:
    v, vt, g, f
    '''

    lvl = levels.level_from_stem(path.stem)
    # if lvl and not levels.validate(lvl):
    #     # print(path.stem, 'does not have a valid filename')
    #     return

    print('  ->', path)

    groups: list[OBJ] = [OBJ()]
    tags: list[str] = []
    face_pts = []

    # read file
    with open(path) as file:
        for line in file:
            line = line.rstrip()
            split = line.split(' ')
            tags.append(split[0])
            match split[0]:
                case Tags.VERT:
                    # ex: v -772 -570 359
                    if len(tags) > 1 and tags[-2] == Tags.FACE:
                        groups.append(OBJ())
                    groups[-1].verts.append(Vert(*[int(s) for s in split[1:]]))
                case Tags.UVW:
                    # ex: vt 0.921569 0.733333 1.000000
                    groups[-1].uvws.append(UVW(*[float(s) for s in split[1:]]))
                case Tags.GROUP:
                    # ex: g sky_1
                    groups[-1].name = split[1]
                case Tags.FACE:
                    # ex: f 10/6 14/4 9/4
                    groups[-1].faces.append(Face.from_str(line))
                    face_pts.append(groups[-1].faces[-1])

    # generate mesh
    bpy.ops.wm.obj_import(filepath=str(path), up_axis='Z', forward_axis='NEGATIVE_X', global_scale=SCALE)
    obj: Object = bpy.context.selected_objects[0]
    if not isinstance(obj.data, Mesh):
        return

    all_uvws = [uvw for group in groups for uvw in group.uvws]
    color = obj.data.color_attributes.new(name='Color', type='BYTE_COLOR', domain='POINT')

    # apply vertex colors
    for vert in obj.data.vertices:
        uvw = get_uvw_from_vert_idx(groups, all_uvws, vert.index)
        if uvw:
            color.data[vert.index].color = (uvw.u, uvw.v, uvw.w, 1.0)  # UVW -> RGB

    # change name
    level = levels.level_from_stem(path.stem)
    if not level:
        print('NO LEVEL NAME FOUND')
        return
    obj.name = level.name

    # separate sky dome/sphere from extras (like planets and stars)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.0005)
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    parts = [o for o in bpy.data.objects if level.name == o.name.split('.')[0]]

    dims = [part.dimensions.x for part in parts]
    dims_sorted = sorted(dims)

    big_triangle = parts[dims.index(dims_sorted[-1])]
    main_sky = parts[dims.index(dims_sorted[-2])]
    big_triangle.name = level.name + ' Triangle'
    main_sky.name = level.name + ' Sky'

    little_pieces = []
    for part in parts:
        large = part == big_triangle or part == main_sky
        bpy.context.scene.collection.objects.unlink(part)
        bpy.data.collections['Skies' if large else 'Extras'].objects.link(part)
        if large:
            part.select_set(False)
        else:
            little_pieces.append(part)

    if little_pieces:
        current_vl = bpy.context.window.view_layer
        bpy.context.window.view_layer = bpy.context.scene.view_layers['Extras']
        bpy.context.view_layer.objects.active = little_pieces[0]
        # join extras
        bpy.ops.object.join()
        bpy.context.object.name = level.name + ' Extras'
        bpy.context.window.view_layer = current_vl

    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')
    # bpy.context.window.view_layer = bpy.context.scene.view_layers['Base']
