import bpy  # type: ignore


def classes():
    from .props import Latex_Props
    from .operators import Latex_CompileAsMesh, Latex_CompileAsGreasePencil
    from .ui import Latex_Panel_3DV

    return (
        Latex_Props,
        Latex_CompileAsMesh,
        Latex_CompileAsGreasePencil,
        Latex_Panel_3DV,
    )


def register():
    from .props import Latex_Props

    for cls in classes():
        bpy.utils.register_class(cls)

    bpy.types.Scene.blend_et_latex = bpy.props.PointerProperty(type=Latex_Props)


def unregister():
    del bpy.types.Scene.blend_et_latex

    for cls in reversed(classes()):
        bpy.utils.unregister_class(cls)
