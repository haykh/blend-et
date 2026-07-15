_needs_reload = "bpy" in locals()

from . import (
    colormaps,
    tools,
    annotations,
    volume,
    fieldlines,
    pointcloud,
    latex,
)

if _needs_reload:
    import importlib

    from .utilities import (
        data as _util_data,
        types as _util_types,
        nodes as _util_nodes,
        materials as _util_materials,
    )

    importlib.reload(_util_data)
    importlib.reload(_util_types)
    importlib.reload(_util_nodes)

    importlib.reload(colormaps)
    importlib.reload(_util_materials)

    importlib.reload(tools)
    importlib.reload(annotations)
    importlib.reload(volume)
    importlib.reload(fieldlines)
    importlib.reload(pointcloud)
    importlib.reload(latex)
    print("Add-on Reloaded")


def register():
    colormaps.register()
    tools.register()
    annotations.register()
    volume.register()
    fieldlines.register()
    pointcloud.register()
    latex.register()


def unregister():
    latex.unregister()
    pointcloud.unregister()
    fieldlines.unregister()
    volume.unregister()
    annotations.unregister()
    tools.unregister()
    colormaps.unregister()


if __name__ == "__main__":
    register()
