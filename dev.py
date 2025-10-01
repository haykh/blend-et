import bpy  # type: ignore
import sys
import importlib

from . import tools, annotations, volume, latex

ADDON_PKG = str(__package__).split(".")[0]

SUBMODULES = (tools, annotations, volume, latex)


def RegisterAll(include_dev=True):
    if include_dev:
        bpy.utils.register_class(Dev_Panel_3DV)
        bpy.utils.register_class(DevReload)

    for m in SUBMODULES:
        m.register()


def UnregisterAll(include_dev=True):
    for m in reversed(SUBMODULES):
        try:
            m.unregister()
        except Exception as e:
            print("unregister failed:", m.__name__, e)

    if include_dev:
        try:
            bpy.utils.unregister_class(DevReload)
        except Exception:
            pass
        try:
            bpy.utils.unregister_class(Dev_Panel_3DV)
        except Exception:
            pass


def _reload_addon_packages():
    """Reload ALL modules under the add-on package, deepest first, except dev itself."""
    prefix = ADDON_PKG + "."
    names = [
        n for n in list(sys.modules.keys()) if n == ADDON_PKG or n.startswith(prefix)
    ]

    names = [n for n in names if n not in (ADDON_PKG + ".dev",)]

    for name in sorted(names, key=len, reverse=True):
        importlib.reload(sys.modules[name])

    from . import (
        tools as _tools,
        annotations as _annotations,
        volume as _volume,
        latex as _latex,
    )

    global SUBMODULES
    SUBMODULES = (_tools, _annotations, _volume, _latex)


class Dev_Panel_3DV(bpy.types.Panel):
    bl_label = "Development"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendET"

    def draw(self, context):
        layout = self.layout
        layout.operator("blend_et.dev_reload", icon="INFO")


class DevReload(bpy.types.Operator):
    bl_idname = "blend_et.dev_reload"
    bl_label = "Reload Blend-ET"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        try:
            UnregisterAll(include_dev=False)

            _reload_addon_packages()

            RegisterAll(include_dev=False)

            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()

            self.report({"INFO"}, "Blend-ET reloaded")
            print("[blend_et] dev_reload complete")
            return {"FINISHED"}
        except Exception as e:
            self.report({"ERROR"}, f"Reload failed: {e}")
            raise
