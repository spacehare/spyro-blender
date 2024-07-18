'''tested in blender 4.1'''

from pathlib import Path
import bpy
from bpy import ops
import math
import bmesh

RESOLUTION = 256
input_paths = [Path(r"I:\Spyro\ripped\Spyro the Dragon 2 Ripto's Rage"),
               Path(r"I:\Spyro\ripped\Spyro the Dragon 1")]
output_path = Path(r'I:\Spyro\renders')
FILENAME = "Sky Vertex Colors.FBX"
sky_paths: list[Path] = []
for path in input_paths:
    for file in path.rglob('*'):
        if file.name == FILENAME:
            sky_paths.append(file)


def extrude_lowest_loop(what: bpy.types.Object):
    ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(what.data)
    min_z = min(v.co.z for v in bm.verts)

    target_edge = None

    for edge in bm.edges:
        for vert in edge.verts:
            if vert.co.z == min_z:
                target_edge = edge
                break

    bpy.ops.mesh.select_all(action='DESELECT')
    target_edge.select = True
    bpy.context.tool_settings.mesh_select_mode = (False, True, False)

    # i cannot for the life of me figure out edge loop selection
    # bpy.ops.mesh.loop_select(extend=True)
    # for loop in target_edge.link_loops:

    bpy.ops.mesh.select_non_manifold()

    bmesh.update_edit_mesh(what.data)
    ops.mesh.extrude_edges_move(
        MESH_OT_extrude_edges_indiv={'mirror': False},
        TRANSFORM_OT_translate={'value': (0, 0, -10)})
    bpy.ops.mesh.edge_face_add()
    bpy.ops.mesh.poke()


def set_rotation(what, x, y, z):
    what.rotation_euler.x = math.radians(x)
    what.rotation_euler.z = math.radians(z)
    what.rotation_euler.y = math.radians(y)


def render(filename: Path):
    bpy.context.scene.render.filepath = str(output_path / filename)
    ops.render.render(write_still=True)


def init_render():
    bpy.context.scene.render.image_settings.color_mode = 'RGB'
    bpy.context.scene.render.image_settings.file_format = 'TARGA'


def init_camera():
    ops.object.camera_add()
    cam = bpy.context.object  # ; bpy.data.objects['Camera'] ; bpy.context.scene.camera
    bpy.context.scene.camera = cam
    cam.location = (0, 0, 0)
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

    ops.import_scene.fbx(filepath=str(path_to_sky), global_scale=0.5, use_manual_orientation=True,  axis_up='Z', axis_forward='-X')

    pieces = bpy.context.selected_objects
    # ops.object.select_all(action='DESELECT')

    # pieces[0].select_set(True)  # sky_0
    # ops.object.delete()

    # ops.object.mode_set(mode='OBJECT')

    for obj in pieces:
        obj.select_set(obj.name != 'sky_0')

    bpy.context.view_layer.objects.active = pieces[1]
    ops.object.join()

    joined = bpy.context.object
    ops.object.transform_apply()
    ops.object.mode_set(mode='EDIT')
    ops.mesh.select_all(action='SELECT')
    ops.mesh.remove_doubles(threshold=0.001)  # 0.0001 is default
    ops.mesh.normals_make_consistent(inside=True)
    joined.data.materials[0] = mat
    extrude_lowest_loop(joined)

    ops.object.mode_set(mode='OBJECT')


mat = init_material()
cam = init_camera()
init_render()

bpy.context.scene.render.resolution_x = RESOLUTION
bpy.context.scene.render.resolution_y = RESOLUTION
bpy.context.scene.view_settings.view_transform = 'Standard'

for sky_path in sky_paths[2:3]:
    init_skybox(sky_path, mat)
    name = sky_path.parent.name[4:].replace(' ', '_')

    # ft - front
    set_rotation(cam, 90, 0, 0)
    render(name + '_ft')

    # rt - right
    set_rotation(cam, 90, 0, 90)
    render(name + '_rt')

    # bk - back
    set_rotation(cam, 90, 0, 180)
    render(name + '_bk')

    # lf - left
    set_rotation(cam, 90, 0, 270)
    render(name + '_lf')

    # up - up
    set_rotation(cam, 180, 0, 90)
    render(name + '_up')

    # dn - down
    set_rotation(cam, 0, 0, 0)
    render(name + '_dn')
