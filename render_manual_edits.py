import bpy
from pathlib import Path
from . import render_sky

'''
this script expects a 2 view layers and 2 collections, sharing the same pair of names
- Skies
- Extras
'''


def render_all(path: Path, res: int = 512, ):
    extras = bpy.data.collections['Extras']
    skies = bpy.data.collections['Skies']
    cam = bpy.context.scene.camera

    for sky in skies.objects:
        stripped: str = sky.name.removesuffix(' Sky')
        possible_extra = extras.objects.find(stripped + ' Extra')

        if possible_extra != -1:
            extra = extras.objects[possible_extra]
            extra.hide_render = False

        sky.hide_render = False

        render_sky.render_skybox(path, stripped, cam, res, stripped != 'Haunted Towers')

        if possible_extra != -1:
            extra.hide_render = True
        sky.hide_render = True
