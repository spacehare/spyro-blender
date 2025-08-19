import bpy
from .swv import NAME_EXTRAS, NAME_SKIES


def setup_compositor(sky_layer_name: str, extra_layer_name: str):
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


def set_render_file_format(fmt: str = 'PNG'):
    '''
    # format types
    - BMP
    - IRIS
    - PNG
    - JPEG
    - JPEG2000
    - TARGA
    - TARGA_RAW
    - CINEON
    - DPX
    - OPEN_EXR_MULTILAYER
    - OPEN_EXR
    - HDR
    - TIFF
    - WEBP
    '''
    # https://docs.blender.org/api/current/bpy_types_enum_items/image_type_items.html
    if not bpy.context.scene:
        return
    bpy.context.scene.render.image_settings.file_format = fmt


def setup_render_settings():
    if not bpy.context.scene:
        return

    bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
    bpy.context.scene.display.shading.light = 'FLAT'
    bpy.context.scene.display.shading.color_type = 'VERTEX'

    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.image_settings.color_mode = 'RGB'
    bpy.context.scene.view_settings.view_transform = 'Raw'


def setup_camera(camera: Object | None = None):
    if not bpy.context.scene:
        return

    cam: Object
    if camera:
        cam = camera
    elif bpy.context.scene.camera:
        cam = bpy.context.scene.camera
    else:
        bpy.ops.object.camera_add()
        cam = bpy.context.object  # ; bpy.data.objects['Camera'] ; bpy.context.scene.camera
    if not bpy.context.scene:
        return

    if cam:
        bpy.context.scene.camera = cam  # make camera active
        bpy.ops.object.location_clear()  # cam.location = (0, 0, 0)
        bpy.ops.object.rotation_clear()
        cam.rotation_mode = 'XYZ'
        # cam.data.type = 'ORTHO'
        # cam.data.ortho_scale = 6.0
        cam.data.lens = 18  # 90 FOV

    return cam


def setup_viewlayers_and_collections():
    if not bpy.context.scene:
        return

    # collections
    possible_skies_collection = bpy.data.collections.get(NAME_SKIES)
    possible_extras_collection = bpy.data.collections.get(NAME_EXTRAS)

    if possible_skies_collection or possible_extras_collection:
        print('collections already exist')
        return
    else:
        collection_skies = bpy.data.collections.new(NAME_SKIES)
        collection_extras = bpy.data.collections.new(NAME_EXTRAS)

        bpy.context.scene.collection.children.link(collection_skies)
        bpy.context.scene.collection.children.link(collection_extras)

    # view layers
    possible_skies_viewlayer = bpy.context.scene.view_layers[NAME_SKIES]
    possible_extras_viewlayer = bpy.context.scene.view_layers[NAME_EXTRAS]

    if possible_skies_viewlayer or possible_extras_viewlayer:
        print('viewlayers already exist')
        return
    else:
        vl_skies = bpy.context.scene.view_layers.new(NAME_SKIES)
        vl_extras = bpy.context.scene.view_layers.new(NAME_EXTRAS)

        vl_skies.layer_collection.children[NAME_EXTRAS].exclude = True
        vl_extras.layer_collection.children[NAME_SKIES].exclude = True

    print('view layers and collections OK')
