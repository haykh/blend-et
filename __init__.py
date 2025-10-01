from .reload import dev_refresh

bl_info = {
    "name": "BlendET",
    "author": "hayk",
    "version": (0, 1, 0),
    "blender": (4, 5, 0),
    "location": "N panel > BlendET",
    "description": "Collection of tools for scientific visualization and rendering.",
    "category": "Object",
}

from . import tools, annotations, volume, latex


def register():
    tools.register()
    annotations.register()
    volume.register()
    latex.register()


def unregister():
    latex.unregister()
    volume.unregister()
    annotations.unregister()
    tools.unregister()


if __name__ == "__main__":
    register()
