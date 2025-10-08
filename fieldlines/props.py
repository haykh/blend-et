import bpy

from .utils import (
    On_material_colormap_change,
)

from ..colormaps.data import (  # pyright: ignore[reportMissingImports]
    Enum_colormap_items,
)


class Fieldlines_Props(bpy.types.PropertyGroup):
    uuid: bpy.props.IntProperty(
        name="UUID",
        description="UUID for the fieldlines",
        default=0,
    )
    npz_path: bpy.props.StringProperty(
        name=".npz",
        description="Path to a 3D NumPy dictionary file with the data",
        subtype="FILE_PATH",
    )


class FieldlineMaterial_Props:
    @staticmethod
    def register():
        if hasattr(bpy.types.Material, "fieldline_colormap"):
            del bpy.types.Material.fieldline_colormap
        if hasattr(bpy.types.Material, "fieldline_colormap_reversed"):
            del bpy.types.Material.fieldline_colormap_reversed
        bpy.types.Material.fieldline_colormap = bpy.props.EnumProperty(
            name="Colormap",
            description="Colormap for the fieldline material",
            items=Enum_colormap_items,
            default=0,
            update=On_material_colormap_change,
        )
        bpy.types.Material.fieldline_colormap_reversed = bpy.props.BoolProperty(
            name="Reverse colormap",
            description="Reverse the selected colormap (like Matplotlib _r)",
            default=False,
            update=On_material_colormap_change,
        )

    @staticmethod
    def unregister():
        if hasattr(bpy.types.Material, "fieldline_colormap_reversed"):
            del bpy.types.Material.fieldline_colormap_reversed
        if hasattr(bpy.types.Material, "fieldline_colormap"):
            del bpy.types.Material.fieldline_colormap
