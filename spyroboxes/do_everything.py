from pathlib import Path
from . import batch
from . import setup


def do_everything(*, should_setup: bool = False, mesh_folder_path: str = '', render_path: str = '', render_xy: int = 0):
    if should_setup:
        setup.set_render_file_format()
        setup.setup_compositor()
        setup.setup_render_settings()
        setup.setup_viewlayers_and_collections()
        setup.setup_camera()

    if mesh_folder_path:
        batch.batch_import_skies(Path(mesh_folder_path), batch.get_groups_whitelist())
        batch.fix_all_verts()

    if render_path and render_xy:
        batch.render_all_skyboxes(Path(render_path), render_xy)
