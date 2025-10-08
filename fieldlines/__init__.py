import bpy


def classes():
    from .props import Fieldlines_Props
    from .operators import (
        Fieldlines_Create,
        FieldlineMaterial_CreateOrReset,
        FieldlineMaterial_ReverseColormap,
    )
    from .ui import FieldlineMaterial_Panel_NDE, Fieldlines_Panel_3DV

    return (
        Fieldlines_Props,
        Fieldlines_Create,
        FieldlineMaterial_CreateOrReset,
        FieldlineMaterial_ReverseColormap,
        FieldlineMaterial_Panel_NDE,
        Fieldlines_Panel_3DV,
    )


def register():
    from .props import Fieldlines_Props
    from .props import FieldlineMaterial_Props

    for cls in classes():
        bpy.utils.register_class(cls)

    bpy.types.Scene.blend_et_fieldlines = bpy.props.PointerProperty(
        type=Fieldlines_Props
    )
    FieldlineMaterial_Props.register()


def unregister():
    from .props import FieldlineMaterial_Props

    FieldlineMaterial_Props.unregister()
    del bpy.types.Scene.blend_et_fieldlines

    for cls in reversed(classes()):
        bpy.utils.unregister_class(cls)
