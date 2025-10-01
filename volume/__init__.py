import bpy  # type: ignore


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
    from .utils import Build_colormap_previews

    for cls in classes():
        bpy.utils.register_class(cls)

    bpy.types.Scene.blend_et_volume_render = bpy.props.PointerProperty(
        type=Volume_Props
    )

    VolumeMaterial_Props.register()

    Build_colormap_previews()


def unregister():
    from .props import VolumeMaterial_Props
    from .utils import Free_colormap_previews

    Free_colormap_previews()

    VolumeMaterial_Props.unregister()

    del bpy.types.Scene.blend_et_volume_render

    for cls in reversed(classes()):
        bpy.utils.unregister_class(cls)
