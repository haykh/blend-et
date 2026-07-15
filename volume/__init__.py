_needs_reload = "bpy" in locals()

import bpy


def classes():
    from .props import Volume_Props
    from .operators import (
        VolumeMaterial_ReverseColormap,
        VolumeMaterial_CreateOrReset,
        Volume_ImportVDB,
        Volume_ImportNumpy,
    )
    from .ui import BLENDET_PT_volume_material_nde, BLENDET_PT_volume_3dv

    return (
        Volume_Props,
        Volume_ImportVDB,
        Volume_ImportNumpy,
        VolumeMaterial_ReverseColormap,
        VolumeMaterial_CreateOrReset,
        BLENDET_PT_volume_3dv,
        BLENDET_PT_volume_material_nde,
    )


def register():
    from .props import Volume_Props, VolumeMaterial_Props

    for cls in classes():
        bpy.utils.register_class(cls)

    bpy.types.Scene.blend_et_volume_render = bpy.props.PointerProperty(
        type=Volume_Props
    )

    VolumeMaterial_Props.register()


def unregister():
    from .props import VolumeMaterial_Props

    VolumeMaterial_Props.unregister()

    del bpy.types.Scene.blend_et_volume_render

    for cls in reversed(classes()):
        bpy.utils.unregister_class(cls)


if _needs_reload:
    import importlib

    from . import utils, props, operators, ui

    importlib.reload(utils)
    importlib.reload(props)
    importlib.reload(operators)
    importlib.reload(ui)
