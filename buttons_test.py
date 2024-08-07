'''this script is not meant to be used inside of blender
its just a helper script for genering entities for TrenchBroom so i can test how skyboxes look in Quake

this code is also very ugly, but it gets the job done............ sorta
'''

import levels
import pyperclip
import re

target_skybox = '''
{
    "classname" "target_skybox"
    "origin" "$X 0 $Z"
    "targetname" "$targetname"
    "sky" "$sky"
}
'''
func_button = '''
{
"classname" "func_button"
"target" "$target"
"angle" "-2"
"speed" "128"
"message" "$target"
// brush 0
{
( -32 0 -64 ) ( -32 1 -64 ) ( -32 0 -63 ) wall_grey_b [ 0 -1 0 -32 ] [ 0 0 -1 0 ] 0 1 1
( -32 0 -64 ) ( -32 0 -63 ) ( -31 0 -64 ) wall_grey_b [ 1 0 0 32 ] [ 0 0 -1 0 ] 0 1 1
( -32 0 -64 ) ( -31 0 -64 ) ( -32 1 -64 ) wall_grey_b [ -1 0 0 -32 ] [ 0 -1 0 -32 ] 0 1 1
( 32 32 -48 ) ( 32 33 -48 ) ( 33 32 -48 ) +0_button [ 1 0 0 0 ] [ 0 -1 0 0 ] 0 1 1
( 32 32 -32 ) ( 33 32 -32 ) ( 32 32 -31 ) wall_grey_b [ -1 0 0 -32 ] [ 0 0 -1 0 ] 0 1 1
( 0 32 -32 ) ( 0 32 -31 ) ( 0 33 -32 ) wall_grey_b [ 0 1 0 32 ] [ 0 0 -1 0 ] 0 1 1
}
}
'''
resolutions = [256, 512, 1024, 2048]
re_xyz = re.compile(r"\( (-?\d+) (-?\d+) (-?\d+) \)")  # or r"(?<=\( )-?\d+""
SHIFT_BY = 64

output = ''

x_shift: int = 0
xyz_count: int = 0
shift_row = 0


def x_a(m):
    global x_shift
    global xyz_count
    global shift_row
    g = m.groups()
    if xyz_count % 18 == 0:
        shift_row += 1
    if xyz_count == 72:
        xyz_count = 0
        x_shift += 64
    xyz_count += 1
    if shift_row == len(resolutions):
        shift_row = 0
    return f'( {int(g[0]) + x_shift} {int(g[1]) + 128 * shift_row} {g[2]} )'


for idx_sky, sky in enumerate(levels.special_skies):
    for idx_res, res in enumerate(resolutions):
        # target_skybox
        target_and_targetname = f"{levels.quake_ok_name(sky.name)}_{res}"
        sb_copy = target_skybox.replace('$X', str(idx_sky * SHIFT_BY))
        sb_copy = sb_copy.replace('$Z', str(idx_res * SHIFT_BY))
        sb_copy = sb_copy.replace('$targetname', target_and_targetname)
        sb_copy = sb_copy.replace('$sky', f"spyro/{levels.quake_ok_name(sky.name)}_{res}_")
        output += sb_copy

        # func_button
        fb_copy = func_button
        fb_copy = fb_copy.replace('$target', target_and_targetname)
        fb_copy = re_xyz.sub(x_a, fb_copy)

        output += fb_copy + '\n'


pyperclip.copy(output)
