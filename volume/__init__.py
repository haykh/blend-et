import bpy


def classes():
    from .props import Volume_Props
    from .operators import (
        VolumeMaterial_ReverseColormap,
        VolumeMaterial_CreateOrReset,
        Volume_ImportVDB,
        Volume_ImportNumpy,
    )
    from .ui import VolumeMaterial_Panel_NDE, Volume_Panel_3DV

    return (
        Volume_Props,
        Volume_ImportVDB,
        Volume_ImportNumpy,
        VolumeMaterial_ReverseColormap,
        VolumeMaterial_CreateOrReset,
        Volume_Panel_3DV,
        VolumeMaterial_Panel_NDE,
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
