bl_info = {
    "name": "BlendET",
    "author": "hayk",
    "version": (0, 1, 0),
    "blender": (4, 5, 0),
    "location": "N panel > BlendET",
    "description": "Collection of tools for scientific visualization and rendering.",
    "category": "Object",
}

from .dev import RegisterAll, UnregisterAll


def register():
    RegisterAll()


def unregister():
    UnregisterAll()


if __name__ == "__main__":
    register()
