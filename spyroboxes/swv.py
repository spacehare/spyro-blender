'''
import the OBJ from SpyroWorldViewer into blender as a mesh.

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
NAME_SKIES = 'Skies'
NAME_EXTRAS = 'Extras'


class Suffixes(StrEnum):
    SKY = 'S'
    COLORS = 'F'
    LOWPOLY = 'L'
    LIGHTSHADE = 'M'
    TEXTURES = 'T'
    LIGHTSHADE_WATER = 'MW'
    TEXTURE_WATER = 'TW'


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


def import_spyro_obj(file_path: Path):
    '''
    - import a raw OBJ file from a path.
      - merge all groups into one mesh.

    SpyroWorldViewer OBJ line order:  
    1. `v`
    2. `vt`
    3. `g`
    4. `f`
    '''

    print('importing SpyroWorldViewer OBJ from:', file_path)

    groups: list[OBJ] = [OBJ()]
    tags: list[str] = []
    face_pts = []

    # read file
    with open(file_path) as file:
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
    bpy.ops.wm.obj_import(filepath=str(file_path), up_axis='Z', forward_axis='NEGATIVE_X', global_scale=SCALE)
    obj: Object = bpy.context.selected_objects[0]
    if not isinstance(obj.data, Mesh):
        return

    # apply vertex colors
    all_uvws = [uvw for group in groups for uvw in group.uvws]
    color = obj.data.color_attributes.new(name='Color', type='BYTE_COLOR', domain='POINT')

    for vert in obj.data.vertices:
        uvw = get_uvw_from_vert_idx(groups, all_uvws, vert.index)
        if uvw:
            color.data[vert.index].color = (uvw.u, uvw.v, uvw.w, 1.0)  # UVW -> RGB

    return obj


def organize_meshes(obj: Object):
    '''
    - edit the object name
    - remove doubles
    - move pieces to distinct collections
    - move pieces to distinct view layers
    '''

    if not isinstance(obj.data, Mesh):
        raise ValueError(f"{obj.name} data must be Mesh")

    print('organizing object: %s' % obj.name)

    # change object's name
    level = levels.level_from_stem(obj.name)
    if not level:
        raise ValueError('NO LEVEL NAME FOUND AT %s' % obj.name)
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

    big_triangle.name = level.name + ' - Tetrahedron'
    main_sky.name = level.name + ' - Sky'

    little_pieces: list[Object] = []
    for part in parts:
        is_part_large: bool = part == big_triangle or part == main_sky
        for collection in part.users_collection:
            collection.objects.unlink(part)
        # bpy.context.scene.collection.objects.unlink(part)
        bpy.data.collections[NAME_SKIES if is_part_large else NAME_EXTRAS].objects.link(part)
        if is_part_large:
            part.select_set(False)
        else:
            little_pieces.append(part)

    if little_pieces:
        bpy.context.view_layer.objects.active = little_pieces[0]
        bpy.ops.object.join()
        bpy.context.object.name = f"{level.name} - {NAME_EXTRAS}"

    bpy.ops.object.select_all(action='DESELECT')
