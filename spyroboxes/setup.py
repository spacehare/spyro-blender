import bpy
from bpy.types import Object
from .swv import NAME_EXTRAS, NAME_SKIES


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
    else:
        collection_skies = bpy.data.collections.new(NAME_SKIES)
        collection_extras = bpy.data.collections.new(NAME_EXTRAS)

        bpy.context.scene.collection.children.link(collection_skies)
        bpy.context.scene.collection.children.link(collection_extras)

    # view layers
    possible_skies_viewlayer = bpy.context.scene.view_layers.get(NAME_SKIES)
    possible_extras_viewlayer = bpy.context.scene.view_layers.get(NAME_EXTRAS)

    if possible_skies_viewlayer or possible_extras_viewlayer:
        print('viewlayers already exist')
    else:
        viewlayer_skies = bpy.context.scene.view_layers.new(NAME_SKIES)
        viewlayer_extras = bpy.context.scene.view_layers.new(NAME_EXTRAS)

        viewlayer_skies.layer_collection.children[NAME_EXTRAS].exclude = True
        viewlayer_extras.layer_collection.children[NAME_SKIES].exclude = True

    print('view layers and collections OK')


def setup_compositor():
    possible_skies_viewlayer = bpy.context.scene.view_layers.get(NAME_SKIES)
    possible_extras_viewlayer = bpy.context.scene.view_layers.get(NAME_EXTRAS)

    if not (possible_extras_viewlayer and possible_skies_viewlayer):
        print('viewlayers need to be set up first!')
        return

    # bpy.context.window.workspace = bpy.data.workspaces['Compositing']
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    if tree:
        ao = tree.nodes.new('CompositorNodeAlphaOver')
        render_layer_skies = tree.nodes.new('CompositorNodeRLayers')
        render_layer_extras = tree.nodes.new('CompositorNodeRLayers')
        render_layer_skies.layer = NAME_SKIES
        render_layer_extras.layer = NAME_EXTRAS

        tree.links.new(render_layer_skies.outputs['Image'], ao.inputs[1])
        tree.links.new(render_layer_extras.outputs['Image'], ao.inputs[2])

        comp = tree.nodes.get('Composite')
        if not comp:
            comp = tree.nodes.new('CompositorNodeComposite')
        tree.links.new(ao.outputs['Image'], comp.inputs[0])
