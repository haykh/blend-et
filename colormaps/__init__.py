_needs_reload = "data" in locals()

from . import data


def register():
    data.Build_colormap_previews()


def unregister():
    data.Free_colormap_previews()


if _needs_reload:
    import importlib

    importlib.reload(data)
