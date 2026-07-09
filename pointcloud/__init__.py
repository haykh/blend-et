import bpy


def classes():
    from .props import Pointcloud_Props
    from .operators import (
        Pointcloud_Create,
        PointcloudMaterial_ReverseColormap,
        PointcloudMaterial_CreateOrReset,
    )
    from .ui import BLENDET_PT_pointcloud_material_nde, BLENDET_PT_pointcloud_3dv

    return (
        Pointcloud_Props,
        Pointcloud_Create,
        PointcloudMaterial_CreateOrReset,
        PointcloudMaterial_ReverseColormap,
        BLENDET_PT_pointcloud_material_nde,
        BLENDET_PT_pointcloud_3dv,
    )


def register():
    from .props import Pointcloud_Props, PointcloudMaterial_Props

    for cls in classes():
        bpy.utils.register_class(cls)

    bpy.types.Scene.blend_et_pointcloud = bpy.props.PointerProperty(
        type=Pointcloud_Props
    )
    PointcloudMaterial_Props.register()


def unregister():
    from .props import PointcloudMaterial_Props

    PointcloudMaterial_Props.unregister()
    del bpy.types.Scene.blend_et_pointcloud

    for cls in reversed(classes()):
        bpy.utils.unregister_class(cls)
