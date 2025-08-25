'''render the vertex skybox as a 6-sided cubemap'''

import bpy
from pathlib import Path
import math


def rotate(what, x, y, z):
    what.rotation_euler.x = math.radians(x)
    what.rotation_euler.z = math.radians(z)
    what.rotation_euler.y = math.radians(y)


def render(output_path: Path, xy: int):
    if bpy.context.scene:
        bpy.context.scene.render.resolution_x = xy
        bpy.context.scene.render.resolution_y = xy
        bpy.context.scene.render.filepath = str(output_path)
        bpy.ops.render.render(write_still=True)


def render_top_preview(*, output_path, res_xy: int = 128):
    name = 'Camera Top-Down'
    cam = bpy.data.objects.get(name)
    if not cam:
        bpy.ops.object.camera_add()
        cam = bpy.context.object
        cam.name = name
    if cam:
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = 65.0
        cam.rotation_euler.x = 0.0
        cam.rotation_euler.y = 0.0
        cam.rotation_euler.z = 0.0
        cam.location.x = 0.0
        cam.location.y = 0.0
        cam.location.z = 128.0
    else:
        print('add a camera!')

    render(output_path, res_xy)


def add_direction(path: Path, direction: str):
    return path.with_stem(f"{path.stem}_{direction}")


def render_skybox(out_folder: Path, file_name: str, cam, res: int, dn_as_1: bool):
    out = out_folder / f"{file_name}"
    print(f'{res}x{res}', out)

    # +Y ft front
    rotate(cam, 90, 0, 0)
    render(add_direction(out, 'ft'), res)

    # +X rt right
    rotate(cam, 90, 0, 90)
    render(add_direction(out, 'rt'), res)

    # -Y bk back
    rotate(cam, 90, 0, 180)
    render(add_direction(out, 'bk'), res)

    # -X lf left
    rotate(cam, 90, 0, 270)
    render(add_direction(out, 'lf'), res)

    # +Z up up
    rotate(cam, 180, 0, 90)
    render(add_direction(out, 'up'), res)

    # -Z dn down
    rotate(cam, 0, 0, 90)
    render(add_direction(out, 'dn'), 1 if dn_as_1 else res)
