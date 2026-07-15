_needs_reload = "bpy" in locals()

import bpy


def classes():
    from .props import Fieldlines_Props
    from .operators import (
        Fieldlines_Create,
        FieldlineMaterial_CreateOrReset,
        FieldlineMaterial_ReverseColormap,
    )
    from .ui import BLENDET_PT_fieldline_material_nde, BLENDET_PT_fieldlines_3dv

    return (
        Fieldlines_Props,
        Fieldlines_Create,
        FieldlineMaterial_CreateOrReset,
        FieldlineMaterial_ReverseColormap,
        BLENDET_PT_fieldline_material_nde,
        BLENDET_PT_fieldlines_3dv,
    )


def register():
    from .props import Fieldlines_Props, FieldlineMaterial_Props

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


if _needs_reload:
    import importlib

    from . import utils, props, operators, ui

    importlib.reload(utils)
    importlib.reload(props)
    importlib.reload(operators)
    importlib.reload(ui)
