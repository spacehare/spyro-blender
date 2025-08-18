import bpy
from pathlib import Path
from . import render_sky


'''
see fixed_skyboxes.blend
'''


def render_all(path: Path, resolutions: list[int], whitelist: list[str] = []):
    if not bpy.context.scene:
        return

    extras = bpy.data.collections['Extras']
    skies = bpy.data.collections['Skies']
    cam = bpy.context.scene.camera

    for sky in [s for s in skies.objects if not whitelist or s.name in whitelist]:
        stripped: str = sky.name.removesuffix(' Sky')
        possible_extra = extras.objects.find(stripped + ' Extra')

        if possible_extra != -1:
            extra = extras.objects[possible_extra]
            extra.hide_render = False

        sky.hide_render = False

        for res in resolutions:
            render_sky.render_skybox(path, stripped, cam, res, stripped != 'Haunted Towers')

        if possible_extra != -1:
            extra.hide_render = True
        sky.hide_render = True
