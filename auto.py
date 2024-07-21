import bpy
import bmesh
from pathlib import Path


def init_compositor(sky_layer_name: str, extra_layer_name: str):
    # bpy.context.window.workspace = bpy.data.workspaces['Compositing']
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    if tree:
        ao = tree.nodes.new('CompositorNodeAlphaOver')
        rl_sky = tree.nodes.new('CompositorNodeRLayers')
        rl_extra = tree.nodes.new('CompositorNodeRLayers')
        rl_sky.layer = sky_layer_name
        rl_extra.layer = extra_layer_name

        tree.links.new(rl_sky.outputs['Image'], ao.inputs[1])
        tree.links.new(rl_extra.outputs['Image'], ao.inputs[2])
        comp = tree.nodes['Composite']
        tree.links.new(ao.outputs['Image'], comp.inputs[0])


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
        bpy.ops.object.camera_add()
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
    '''for EEVEE rendering'''
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


def init_skybox(path_to_sky: Path, collection_skies: bpy.types.Collection, collection_extras: bpy.types.Collection, extrude=True, mat=None):
    bpy.ops.object.select_all(action='DESELECT')

    bpy.ops.import_scene.fbx(filepath=str(path_to_sky), global_scale=1, use_manual_orientation=True,  axis_up='Z', axis_forward='-X')

    pieces = bpy.context.selected_objects

    # get rid of the huge triangle surrounding the dome
    bpy.ops.object.select_all(action='DESELECT')
    pieces[0].select_set(True)  # sky_0
    bpy.ops.object.delete()
    pieces.pop(0)

    for obj in pieces:
        obj.select_set(True)  # obj.select_set(obj.name != 'sky_0')

    # join all the chunks/pieces
    bpy.context.view_layer.objects.active = pieces[0]
    bpy.ops.object.join()

    NAME_GENERAL = 'dome_pieces'
    NAME_DOME = 'dome'

    joined = bpy.context.object
    joined.name = NAME_GENERAL
    bpy.ops.object.transform_apply()
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.0005)  # 0.0001 is default
    bpy.ops.mesh.normals_make_consistent(inside=True)
    if mat:
        joined.data.materials[0] = mat

    # separate sky dome/sphere from loose geo, like stars and planets (ex: Glimmer)
    bpy.ops.mesh.separate(type='LOOSE')

    # get the main dome
    relevant_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH' and NAME_GENERAL in obj.name]
    dims = [obj.dimensions.x for obj in relevant_objects]
    sky_geo = relevant_objects[dims.index(max(dims))]
    sky_geo.name = NAME_DOME

    for r_obj in relevant_objects:
        bpy.data.collections['Collection'].objects.unlink(r_obj)
        if r_obj == sky_geo:
            collection_skies.objects.link(r_obj)
        else:
            collection_extras.objects.link(r_obj)

    if extrude:
        extrude_lowest_loop(sky_geo)

    bpy.ops.object.mode_set(mode='OBJECT')


def init_viewlayers_and_collections():
    NAME_SKIES = 'Skies'
    NAME_EXTRAS = 'Extras'
    collection_skies = bpy.data.collections.new(NAME_SKIES)
    collection_extras = bpy.data.collections.new(NAME_EXTRAS)
    bpy.context.scene.collection.children.link(collection_skies)
    bpy.context.scene.collection.children.link(collection_extras)
    vl_sky = bpy.context.scene.view_layers.new(NAME_SKIES)
    vl_ext = bpy.context.scene.view_layers.new(NAME_EXTRAS)
    vl_sky.layer_collection.children[NAME_EXTRAS].exclude = True
    vl_ext.layer_collection.children[NAME_SKIES].exclude = True

    print('view layers and collections OK')

    return collection_skies, collection_extras


def extrude_lowest_loop(what: bpy.types.Object):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    what.select_set(True)
    bpy.context.view_layer.objects.active = what
    bpy.ops.object.mode_set(mode='EDIT')

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
    # bpy.bpy.ops.mesh.loop_select()
    # for loop in target_edge.link_loops

    bpy.ops.mesh.select_non_manifold()

    bmesh.update_edit_mesh(what.data)
    bpy.ops.mesh.extrude_edges_move(
        MESH_OT_extrude_edges_indiv={'mirror': False},
        TRANSFORM_OT_translate={'value': (0, 0, -10)})
    bpy.ops.mesh.edge_face_add()
    bpy.ops.mesh.poke()
