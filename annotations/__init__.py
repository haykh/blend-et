import bpy


def classes():
    from .props import Annotations_Props
    from .operators import (
        Annotations_AddAxesGrid,
        Annotations_AddArrow,
        Annotations_AddAxes,
    )
    from .ui import Annotations_Panel_3DV

    return (
        Annotations_Props,
        Annotations_AddAxesGrid,
        Annotations_AddArrow,
        Annotations_AddAxes,
        Annotations_Panel_3DV,
    )


def register():
    from .props import Annotations_Props

    for cls in classes():
        bpy.utils.register_class(cls)

    bpy.types.Scene.blend_et_annotations = bpy.props.PointerProperty(
        type=Annotations_Props
    )


def unregister():
    del bpy.types.Scene.blend_et_annotations

    for cls in reversed(classes()):
        bpy.utils.unregister_class(cls)
