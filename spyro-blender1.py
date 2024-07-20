'''tested in blender 4.1'''

from pathlib import Path
import math
import bpy
from bpy import ops
import bmesh

from . import render_sky

input_paths = [Path(r"I:\Spyro\ripped\Spyro the Dragon 2 Ripto's Rage"),
               Path(r"I:\Spyro\ripped\Spyro the Dragon 1")]
output_path = Path(r"I:\Spyro\renders")
FILENAME = "Sky Vertex Colors.FBX"
sky_paths: list[Path] = []
for path in input_paths:
    for file in path.rglob('*'):
        if file.name == FILENAME:
            sky_paths.append(file)

# init view layers, collections
NAME_SKIES = 'Skies'
NAME_EXTRAS = 'Extras'
collection_skies = bpy.data.collections.new(NAME_SKIES)
collection_extras = bpy.data.collections.new(NAME_EXTRAS)
view_layer_skies = bpy.context.scene.view_layers.new(NAME_SKIES)
view_layer_extras = bpy.context.scene.view_layers.new(NAME_EXTRAS)
# view_layer_extras.layer_collection.exclude(collection_skies)
# view_layer_skies.layer_collection.exclude(collection_extras)


def init_compositor():
    # bpy.context.window.workspace = bpy.data.workspaces['Compositing']
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree

    ao = tree.nodes.new('CompositorNodeAlphaOver')
    rl_sky = tree.nodes.new('CompositorNodeRLayers')
    rl_extra = tree.nodes.new('CompositorNodeRLayers')
    rl_sky.layer = NAME_SKIES
    rl_extra.layer = NAME_EXTRAS

    tree.links.new(rl_sky.outputs['Image'], ao.inputs[1])
    tree.links.new(rl_extra.outputs['Image'], ao.inputs[2])
    comp = tree.nodes['Composite']
    tree.links.new(ao.outputs['Image'], comp.inputs[0])


debug_delete = False
debug_extrude = False
debug_render = False

ignore = ["Crush's Dungeon",  # its just full black
          "Breeze Harbor",  # non-manifold edge toward +X, "merge at last" back into place. also rotate a saturn-like planet's ring to stop z-fighting
          "Gnasty's Loot",  # some kind of extrusion issue ? also fix the saturn-like planet's ring
          "Misty Bog",  # non-manifold pair of verts, "merge at center"
          "Night Flight",  # dissolve vert on a crystal. merge another 2 verts
          "Town Square",  # "merge at center" on 2 pairs of verts
          "Twilight Harbor",  # extrusion issue ? not sure how to diagnose it, so im just manually doing the extrusion steps myself
          "Autumn Plains",  # extrusion not uniform color, made an extra edge loop to tighten the vertex colors
          "Gulp's Overlook",  # extrusion not uniform color
          "Hurricos",  # the ripped sky might have borked vert colors? i'm not confident enough to manually repaint it
          "Haunted Towers",  # ripped sky has some borked vert painting -- easier to fix using a Smear in Vertex Paint mode
          ]
# these are spheres
no_extrude = ["Jacques", "Lofty Castle", "Dark Passage", "Dream Weaver's World", "Gnasty Gnorc", "Haunted Towers"]

'''
manual fix generic steps:
CTRL J = join objects
merge verts at 0.0005
E Z -1 = extrude base of domes -1, scale z to 0 to flatten it
F (F2 addon) = create new face from edge loop

dealing with extra geo...
CTRL+L = select linked
P S = separate by selection
move extraneous geo to separate view layer (stars, planets, etc)
composite extraneous geo over dome/sphere sky

on the "extras" view layer
Scene -> Render -> Film:  Transparent

render method 1
Render Engine: Workbench
Lighting: Flat
Color: Attribute

then we don't even need the shader

render method 2
Render Engine: EEVEE
'''


def trim_parent(path: Path):
    return path.parent.name[4:]


def extrude_lowest_loop(what: bpy.types.Object):
    ops.object.mode_set(mode='OBJECT')
    ops.object.select_all(action='DESELECT')
    what.select_set(True)
    bpy.context.view_layer.objects.active = what
    ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(what.data)
    min_z = min(v.co.z for v in bm.verts)

    target_edge = None

    for edge in bm.edges:
        for vert in edge.verts:
            if vert.co.z == min_z:
                target_edge = edge
                break

    ops.mesh.select_all(action='DESELECT')
    target_edge.select = True
    bpy.context.tool_settings.mesh_select_mode = (False, True, False)

    # i cannot for the life of me figure out edge loop selection
    # bpy.ops.mesh.loop_select(extend=True)
    # for loop in target_edge.link_loops:

    ops.mesh.select_non_manifold()

    bmesh.update_edit_mesh(what.data)
    ops.mesh.extrude_edges_move(
        MESH_OT_extrude_edges_indiv={'mirror': False},
        TRANSFORM_OT_translate={'value': (0, 0, -10)})
    ops.mesh.edge_face_add()
    ops.mesh.poke()


def init_render(workbench=True):
    if workbench:
        bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
        bpy.context.scene.display.shading.light = 'FLAT'
        bpy.context.scene.display.shading.color_type = 'VERTEX'
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.image_settings.color_mode = 'RGB'
    bpy.context.scene.render.image_settings.file_format = 'TARGA'
    bpy.context.scene.view_settings.view_transform = 'Standard'


def init_camera(camera=None):
    if camera:
        cam = camera
    else:
        ops.object.camera_add()
        cam = bpy.context.object  # ; bpy.data.objects['Camera'] ; bpy.context.scene.camera
    bpy.context.scene.camera = cam  # make camera active
    # cam.location = (0, 0, 0)
    bpy.ops.object.location_clear()
    bpy.ops.object.rotation_clear()
    cam.rotation_mode = 'XYZ'
    # cam.data.type = 'ORTHO'
    # cam.data.ortho_scale = 6.0
    cam.data.lens = 18  # 90 FOV

    return cam


def init_material():
    mat = bpy.data.materials.new(name='vertexColors')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # clear defaults
    for node in nodes:
        nodes.remove(node)

    emissive = nodes.new('ShaderNodeEmission')
    output = nodes.new('ShaderNodeOutputMaterial')
    vertex_color = nodes.new('ShaderNodeVertexColor')
    vertex_color.layer_name = 'Attribute'

    links.new(emissive.outputs['Emission'], output.inputs['Surface'])
    links.new(vertex_color.outputs['Color'], emissive.inputs['Color'])

    return mat


def init_skybox(path_to_sky: Path, mat):
    ops.object.select_all(action='DESELECT')

    ops.import_scene.fbx(filepath=str(path_to_sky), global_scale=1, use_manual_orientation=True,  axis_up='Z', axis_forward='-X')

    pieces = bpy.context.selected_objects

    # get rid of the huge triangle surrounding the dome
    ops.object.select_all(action='DESELECT')
    pieces[0].select_set(True)  # sky_0
    ops.object.delete()
    pieces.pop(0)

    for obj in pieces:
        obj.select_set(True)  # obj.select_set(obj.name != 'sky_0')

    # join all the chunks/pieces
    bpy.context.view_layer.objects.active = pieces[0]
    ops.object.join()

    NAME_GENERAL = 'dome_pieces'
    NAME_DOME = 'dome'

    joined = bpy.context.object
    joined.name = NAME_GENERAL
    ops.object.transform_apply()
    ops.object.mode_set(mode='EDIT')
    ops.mesh.select_all(action='SELECT')
    ops.mesh.remove_doubles(threshold=0.0005)  # 0.0001 is default
    ops.mesh.normals_make_consistent(inside=True)
    joined.data.materials[0] = mat

    # separate sky dome/sphere from loose geo, like stars and planets (ex: Glimmer)
    ops.mesh.separate(type='LOOSE')

    # get the main dome
    relevant_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH' and NAME_GENERAL in obj.name]
    dims = [obj.dimensions.x for obj in relevant_objects]
    sky_geo = relevant_objects[dims.index(max(dims))]
    sky_geo.name = NAME_DOME

    # sky_geo.scale = (2, 2, 2)
    collection_skies.objects.link(sky_geo)

    if debug_extrude and trim_parent(path_to_sky) not in no_extrude:
        extrude_lowest_loop(sky_geo)

    ops.object.mode_set(mode='OBJECT')


def clean_up():
    # clean up for next sky
    if debug_delete:
        ops.object.select_all(action='SELECT')
        # bpy.data.objects['sky_0'].select_set(True)
        bpy.data.objects['Camera'].select_set(False)
        ops.object.delete()


def main():
    mat = init_material()
    cam = init_camera()
    init_render()

    for sky_path in sky_paths:
        trimmed = trim_parent(sky_path)
        if trimmed not in ignore:
            init_skybox(sky_path, mat)
        print('  ->', sky_path)
        if debug_render:
            render_sky.render_skybox(output_path / trimmed.replace(' ', '_'), cam, 256, trimmed in no_extrude)
        clean_up()

    if debug_delete:
        bpy.data.objects['Camera'].select_set(True)
        ops.object.delete()
