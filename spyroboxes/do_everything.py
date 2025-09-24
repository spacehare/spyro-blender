from pathlib import Path
from . import batch
from . import setup


def do_everything(*, should_setup: bool = False, mesh_folder_path: str = ''):
    if should_setup:
        setup.set_render_file_format()
        setup.setup_render_settings()
        setup.setup_viewlayers_and_collections()
        setup.setup_compositor()
        setup.setup_camera()

    if mesh_folder_path:
        batch.batch_import_skies(Path(mesh_folder_path), batch.get_groups_whitelist())
        batch.fix_all_verts()
