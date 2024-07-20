'''tested in blender 4.1'''

from pathlib import Path
import bpy

from . import auto
from . import render_sky

input_paths = [Path(r"I:\Spyro\ripped\Spyro the Dragon 2 Ripto's Rage"),
               Path(r"I:\Spyro\ripped\Spyro the Dragon 1")]
output_path = Path(r"I:\Spyro\renders_auto")
FILENAME = "Sky Vertex Colors.FBX"
sky_paths: list[Path] = []
for path in input_paths:
    for file in path.rglob('*'):
        if file.name == FILENAME:
            sky_paths.append(file)


debug_delete = True
debug_render = True

ignore = ["Crush's Dungeon",  # its just full black
          "Breeze Harbor",  # non-manifold edge toward +X, "merge at last" back into place. also rotate a saturn-like planet's ring to stop z-fighting
          "Gnasty's Loot",  # some kind of extrusion issue ? also fix the saturn-like planet's ring
          "Misty Bog",  # non-manifold pair of verts, "merge at center"
          "Night Flight",  # dissolve vert on a crystal. merge another 2 verts
          "Town Square",  # "merge at center" on 2 pairs of verts
          "Twilight Harbor",  # extrusion issue ? not sure how to diagnose it, so im just manually doing the extrusion steps myself
          "Autumn Plains World",  # extrusion not uniform color, made an extra edge loop to tighten the vertex colors
          "Gulp's Overlook",  # extrusion not uniform color
          "Hurricos",  # the ripped sky might have borked vert colors? i'm not confident enough to manually repaint it
          "Haunted Towers",  # ripped sky has some borked vert painting -- easier to fix using a Smear in Vertex Paint mode
          "High Caves",  # extrusion error ?
          ]
# these are spheres
no_extrude = ["Jacques", "Lofty Castle", "Dark Passage", "Dream Weaver's World", "Gnasty Gnorc", "Haunted Towers"]

'''
manual fix generic steps (also see fixed_skyboxes.blend):
CTRL J = join objects
merge verts at 0.0005
E Z -10 = extrude base of domes -1, scale z to 0 to flatten it
F (F2 addon) = create new face from bottom edge loop, if sky is a dome

dealing with extra geo...
CTRL+L = select linked
P S = separate by selection
move extraneous geo to separate Extras view layer (stars, planets, etc)
composite extraneous geo over dome/sphere sky

Scene -> Render -> Film: Transparent

Render Engine: Workbench
Lighting: Flat
Color: Attribute

then we don't even need a shader
'''


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
        if trimmed not in ignore:
            auto.init_skybox(sky_path, c_skies, c_extras, trimmed not in no_extrude)
            if debug_render:
                for res in resolutions:
                    render_sky.render_skybox(output_path, trimmed, cam, res, trimmed not in no_extrude)
        clean_up()

    if debug_delete:
        bpy.data.objects['Camera'].select_set(True)
        bpy.ops.object.delete()
