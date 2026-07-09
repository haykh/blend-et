import bpy


def classes():
    from .props import Latex_Props
    from .operators import Latex_CompileAsMesh, Latex_CompileAsGreasePencil
    from .ui import BLENDET_PT_latex_3dv

    return (
        Latex_Props,
        Latex_CompileAsMesh,
        Latex_CompileAsGreasePencil,
        BLENDET_PT_latex_3dv,
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
