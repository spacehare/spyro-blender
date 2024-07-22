import bpy
from pathlib import Path
import math
from .special_skies import quake_ok_name


def rotate(what, x, y, z):
    what.rotation_euler.x = math.radians(x)
    what.rotation_euler.z = math.radians(z)
    what.rotation_euler.y = math.radians(y)


def render(output_path: Path, xy: int):
    bpy.context.scene.render.resolution_x = xy
    bpy.context.scene.render.resolution_y = xy
    bpy.context.scene.render.filepath = str(output_path)
    bpy.ops.render.render(write_still=True)


def add_dir(path: Path, dir: str):
    return path.with_stem(f"{path.stem}_{dir}")


def render_skybox(out_folder: Path, sky_name: str, cam, res: int, dn_as_1: bool):
    out = out_folder / f"{quake_ok_name(sky_name)}_{res}"
    print(f'{res}x{res}', out)

    # +Y ft front
    rotate(cam, 90, 0, 0)
    render(add_dir(out, 'ft'), res)

    # +X rt right
    rotate(cam, 90, 0, 90)
    render(add_dir(out, 'rt'), res)

    # -Y bk back
    rotate(cam, 90, 0, 180)
    render(add_dir(out, 'bk'), res)

    # -X lf left
    rotate(cam, 90, 0, 270)
    render(add_dir(out, 'lf'), res)

    # +Z up up
    rotate(cam, 180, 0, 90)
    render(add_dir(out, 'up'), res)

    # -Z dn down
    rotate(cam, 0, 0, 90)
    render(add_dir(out, 'dn'), 1 if dn_as_1 else res)
