import bpy  # type: ignore

from .props import Tools_Props
from .operators import Tools_SwitchToCycles, Tools_FixColors, Tools_SetBackground
from .ui import Tools_Panel_3DV

classes = (
    Tools_Props,
    Tools_SwitchToCycles,
    Tools_FixColors,
    Tools_SetBackground,
    Tools_Panel_3DV,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.blend_et_tools = bpy.props.PointerProperty(type=Tools_Props)


def unregister():
    del bpy.types.Scene.blend_et_tools

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
