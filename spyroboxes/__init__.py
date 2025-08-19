bl_info = {
    "name": "Spyroboxes",
    "blender": (4, 4, 3),
    "category": "Generic",
}


def register():
    print('registered spyroboxes')


def unregister():
    print('unregistered spyroboxes')

    # https://blender.stackexchange.com/a/309323
    import importlib
    import sys

    current_package_prefix = f"{__name__}."
    for name, module in sys.modules.copy().items():
        if name.startswith(current_package_prefix):
            print(f"Reloading {name}")
            importlib.reload(module)
