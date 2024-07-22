'''tested in blender 4.1'''

from pathlib import Path
import bpy

from . import auto
from . import render_sky
from . import special_skies

input_paths = [Path(r"I:\Spyro\ripped\Spyro the Dragon 2 Ripto's Rage"),
               Path(r"I:\Spyro\ripped\Spyro the Dragon 1")]
output_path = Path(r"I:\Spyro\renders")
FILENAME = "Sky Vertex Colors.FBX"
sky_paths: list[Path] = []
for path in input_paths:
    for file in path.rglob('*'):
        if file.name == FILENAME:
            sky_paths.append(file)


debug_delete = True
debug_render = True

# these are spheres
no_extrude = ["Jacques", "Lofty Castle", "Dark Passage", "Dream Weaver's World", "Gnasty Gnorc", "Haunted Towers"]


def trim_parent(path: Path):
    return path.parent.name[4:]


def clean_up():
    # clean up for next sky
    if debug_delete:
        bpy.ops.object.select_all(action='SELECT')
        # bpy.data.objects['sky_0'].select_set(True)
        bpy.data.objects['Camera'].select_set(False)
        bpy.ops.object.delete()


def main(resolutions: list[int]):
    c_skies, c_extras = auto.init_viewlayers_and_collections()
    cam = auto.init_camera()
    auto.init_render()
    auto.init_compositor(c_skies.name, c_extras.name)

    for sky_path in sky_paths:  # [sp for sp in sky_paths if 'Dark Passage' in str(sp)]
        trimmed = trim_parent(sky_path)
        if trimmed not in [n.name for n in special_skies.skies if n.manual]:
            auto.init_skybox(sky_path, c_skies, c_extras, trimmed not in no_extrude)
            if debug_render:
                for res in resolutions:
                    render_sky.render_skybox(output_path, trimmed, cam, res, trimmed not in [n.name for n in special_skies.skies if n.is_sphere])
        clean_up()

    if debug_delete:
        bpy.data.objects['Camera'].select_set(True)
        bpy.ops.object.delete()
