_needs_reload = "bpy" in locals()

import bpy


def classes():
    from .props import Tools_Props
    from .operators import (
        Tools_SwitchToCycles,
        Tools_FixColors,
        Tools_SetBackground,
        Tools_ClearUnusedData,
    )
    from .ui import BLENDET_PT_tools_3dv

    return (
        Tools_Props,
        Tools_SwitchToCycles,
        Tools_FixColors,
        Tools_SetBackground,
        Tools_ClearUnusedData,
        BLENDET_PT_tools_3dv,
    )


def register():
    from .props import Tools_Props

    for cls in classes():
        bpy.utils.register_class(cls)

    bpy.types.Scene.blend_et_tools = bpy.props.PointerProperty(type=Tools_Props)


def unregister():
    del bpy.types.Scene.blend_et_tools

    for cls in reversed(classes()):
        bpy.utils.unregister_class(cls)


if _needs_reload:
    import importlib

    from . import props, operators, ui

    importlib.reload(props)
    importlib.reload(operators)
    importlib.reload(ui)
