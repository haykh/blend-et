import bpy

from .utils import (
    On_material_colormap_change,
)

from ..utilities.materials import (
    CommonMaterial_Props,
)


class Pointcloud_Props(bpy.types.PropertyGroup):
    uuid: bpy.props.IntProperty(
        name="UUID",
        description="UUID for the pointcloud object",
        default=0,
    )

    pointcloud_path: bpy.props.StringProperty(
        name=".npz / .csv",
        description="Path to a .npz or .csv file for pointcloud rendering",
        subtype="FILE_PATH",
    )


class PointcloudMaterial_Props:
    @staticmethod
    def register():
        CommonMaterial_Props.register(
            category="pointcloud",
            on_material_change=On_material_colormap_change,
        )

    @staticmethod
    def unregister():
        CommonMaterial_Props.unregister(category="pointcloud")
