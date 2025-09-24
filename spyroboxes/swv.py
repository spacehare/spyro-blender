'''
import the OBJ from SpyroWorldViewer into blender as a mesh.

https://en.wikipedia.org/wiki/Wavefront_.obj_file
'''

import bpy
from bpy.types import Object, Mesh
from pathlib import Path
from typing import NamedTuple
from enum import StrEnum
from dataclasses import dataclass

SCALE = 1/10
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


class Face(NamedTuple):
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


def import_spyro_obj(file_path: Path, *, scale: float | int = SCALE) -> Object:
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
    bpy.ops.wm.obj_import(
        filepath=str(file_path),
        up_axis='Z',
        forward_axis='NEGATIVE_X',
        global_scale=scale,
        import_vertex_groups=True,
    )
    bpy.ops.object.transform_apply()
    obj: Object = bpy.context.selected_objects[0]
    assert (isinstance(obj.data, Mesh))

    # apply vertex colors
    all_uvws = [uvw for group in groups for uvw in group.uvws]
    color = obj.data.color_attributes.new(name='Color', type='BYTE_COLOR', domain='POINT')

    for group in groups:
        for face in group.faces:
            for i in face:
                uvw = all_uvws[i.vt_idx]
                color.data[i.v_idx].color = (uvw.u, uvw.v, uvw.w, 1.0)  # UVW -> RGB

    return obj


def organize_meshes(obj: Object, new_name: str, merge_exceptions: list[int]):
    '''
    - edit the object name
    - remove doubles
    - move pieces to distinct collections
    - move pieces to distinct view layers
    '''

    assert (isinstance(obj.data, Mesh))
    print('organizing object: %s' % obj.name)

    # change object's name
    obj.name = new_name

    # separate sky dome/sphere from extras (like planets and stars)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=True)

    # https://blender.stackexchange.com/questions/75223/finding-vertices-in-a-vertex-group-using-blenders-python-api
    for idx in merge_exceptions:
        obj.vertex_groups.active = obj.vertex_groups[idx]
        bpy.ops.object.vertex_group_deselect()

    bpy.ops.mesh.remove_doubles(threshold=0.0005)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    parts = [o for o in bpy.context.selected_objects]

    dims = [part.dimensions.x for part in parts]
    dims_sorted = sorted(dims)

    big_triangle = parts[dims.index(dims_sorted[-1])]
    main_sky = parts[dims.index(dims_sorted[-2])]

    big_triangle.name = new_name + '_tetrahedron'
    main_sky.name = new_name + '_sky'

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

    extras: Object | None = None
    if little_pieces:
        bpy.context.view_layer.objects.active = little_pieces[0]
        bpy.ops.object.join()
        bpy.context.object.name = f"{new_name}_extras"
        extras = bpy.context.object

    bpy.ops.object.select_all(action='DESELECT')

    return main_sky, big_triangle, extras
