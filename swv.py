'''
https://en.wikipedia.org/wiki/Wavefront_.obj_file
'''

import bpy
import bmesh
import re
from pathlib import Path
from typing import NamedTuple
from enum import StrEnum
from dataclasses import dataclass, field, fields

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


@dataclass
class Vert:
    x: int
    y: int
    z: int


@dataclass
class UVW:
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
    def __init__(self, name: str = '', uvws: list[UVW] = None, verts: list[Vert] = None, faces: list[Face] = None):
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


def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    # https://stackoverflow.com/a/16090640
    return [int(text) if text.isdigit() else text.lower()
            for text in _nsre.split(s)]


def import_spyro_obj(path: Path):
    '''
    the order of the lines in the OBJ files exported by SpyroWorldViewer is:
    v, vt, g, f
    '''
    print('~' * 50)

    groups: list[OBJ] = [OBJ()]
    tags: list[str] = []

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

    # generate mesh
    bpy.ops.wm.obj_import(filepath=str(path), up_axis='Z', forward_axis='NEGATIVE_X', global_scale=SCALE, use_split_groups=True)
    pieces = bpy.context.selected_objects
    all_verts = [vert for group in groups for vert in group.verts]
    all_uvws = [uvw for group in groups for uvw in group.uvws]
    pieces.sort(key=lambda x: natural_sort_key(x.name))
    # groups.sort(key=lambda x: x.name)

    i = 0
    for piece, group in zip(pieces, groups, strict=True):
        color = piece.data.color_attributes.new(name='Color', type='BYTE_COLOR', domain='POINT')

        print(piece.name, len(piece.data.vertices), group.name, len(group.verts))
        for p_v, g_v in zip(piece.data.vertices, group.verts, strict=True):
            uvw = get_uvw_from_vert_idx(groups, all_uvws, i)
            color.data[p_v.index].color = (uvw.u, uvw.v, uvw.w, 1.0)  # UVW -> RGB
            i += 1