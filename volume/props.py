import bpy

from .utils import (
    On_material_colormap_change,
)

from ..colormaps.data import (  # pyright: ignore[reportMissingImports]
    Enum_colormap_items,
)


class Volume_Props(bpy.types.PropertyGroup):
    uuid: bpy.props.IntProperty(
        name="UUID",
        description="UUID for the volume object",
        default=0,
    )

    vdb_path: bpy.props.StringProperty(
        name=".vdb",
        description="Path to .vdb file for volume rendering",
        subtype="FILE_PATH",
    )
    save_relative: bpy.props.BoolProperty(
        name="Store relative path",
        description="Store .vdb filepath relative to this .blend",
        default=False,
    )
    numpy_path: bpy.props.StringProperty(
        name=".npy / .npz",
        description="Path to a 3D NumPy array file",
        subtype="FILE_PATH",
    )
    npz_key: bpy.props.StringProperty(
        name="NPZ field",
        description="Dataset key inside .npz (leave empty for .npy)",
        default="",
    )
    numpy_axis_order: bpy.props.EnumProperty(
        name="Axis order",
        description="Order of axes in the input array",
        items=[
            ("ZYX", "ZYX (common)", "Array is (Z, Y, X)"),
            ("XYZ", "XYZ", "Array is (X, Y, Z)"),
            ("YZX", "YZX", "Array is (Y, Z, X)"),
            ("ZXY", "ZXY", "Array is (Z, X, Y)"),
            ("XZY", "XZY", "Array is (X, Z, Y)"),
            ("YXZ", "YXZ", "Array is (Y, X, Z)"),
        ],
        default="ZYX",
    )
    numpy_crop_xmin: bpy.props.IntProperty(
        name="X min",
        description="Crop array: minimum X index (inclusive)",
        default=0,
    )
    numpy_crop_xmax: bpy.props.IntProperty(
        name="X max",
        description="Crop array: maximum X index (exclusive)",
        default=-1,
    )
    numpy_crop_ymin: bpy.props.IntProperty(
        name="Y min",
        description="Crop array: minimum Y index (inclusive)",
        default=0,
    )
    numpy_crop_ymax: bpy.props.IntProperty(
        name="Y max",
        description="Crop array: maximum Y index (exclusive)",
        default=-1,
    )
    numpy_crop_zmin: bpy.props.IntProperty(
        name="Z min",
        description="Crop array: minimum Z index (inclusive)",
        default=0,
    )
    numpy_crop_zmax: bpy.props.IntProperty(
        name="Z max",
        description="Crop array: maximum Z index (exclusive)",
        default=-1,
    )


class VolumeMaterial_Props:
    @staticmethod
    def register():
        if hasattr(bpy.types.Material, "volume_colormap"):
            del bpy.types.Material.volume_colormap
        if hasattr(bpy.types.Material, "volume_colormap_reversed"):
            del bpy.types.Material.volume_colormap_reversed
        if hasattr(bpy.types.Material, "volume_hist_vmin"):
            del bpy.types.Material.volume_hist_vmin
        if hasattr(bpy.types.Material, "volume_hist_vmax"):
            del bpy.types.Material.volume_hist_vmax
        if hasattr(bpy.types.Material, "volume_hist_q05"):
            del bpy.types.Material.volume_hist_q05
        if hasattr(bpy.types.Material, "volume_hist_q95"):
            del bpy.types.Material.volume_hist_q95
        if hasattr(bpy.types.Material, "volume_hist_image"):
            del bpy.types.Material.volume_hist_image
        if hasattr(bpy.types.Material, "volume_hist_ready"):
            del bpy.types.Material.volume_hist_ready
        bpy.types.Material.volume_colormap = bpy.props.EnumProperty(
            name="Colormap",
            description="Colormap for the volume material",
            items=Enum_colormap_items,
            default=0,
            update=On_material_colormap_change,
        )
        bpy.types.Material.volume_colormap_reversed = bpy.props.BoolProperty(
            name="Reverse colormap",
            description="Reverse the selected colormap (like Matplotlib _r)",
            default=False,
            update=On_material_colormap_change,
        )
        bpy.types.Material.volume_hist_vmin = bpy.props.FloatProperty(
            name="Min value",
            description="Smallest value of imported NumPy data",
            default=0.0,
            precision=6,
        )
        bpy.types.Material.volume_hist_vmax = bpy.props.FloatProperty(
            name="Max value",
            description="Largest value of imported NumPy data",
            default=1.0,
            precision=6,
        )
        bpy.types.Material.volume_hist_q05 = bpy.props.FloatProperty(
            name="5% lows",
            description="Smallest 5% of imported NumPy data",
            default=0.0,
            precision=6,
        )
        bpy.types.Material.volume_hist_q95 = bpy.props.FloatProperty(
            name="5% highs",
            description="Largest 5% of imported NumPy data",
            default=1.0,
            precision=6,
        )
        bpy.types.Material.volume_hist_image = bpy.props.PointerProperty(
            name="Histogram",
            type=bpy.types.Image,
            description="Histogram preview image",
        )
        bpy.types.Material.volume_hist_ready = bpy.props.BoolProperty(
            name="Histogram Ready",
            description="True if histogram comes from NumPy import",
            default=False,
        )

    @staticmethod
    def unregister():
        if hasattr(bpy.types.Material, "volume_hist_ready"):
            del bpy.types.Material.volume_hist_ready
        if hasattr(bpy.types.Material, "volume_hist_image"):
            del bpy.types.Material.volume_hist_image
        if hasattr(bpy.types.Material, "volume_hist_q95"):
            del bpy.types.Material.volume_hist_q95
        if hasattr(bpy.types.Material, "volume_hist_q05"):
            del bpy.types.Material.volume_hist_q05
        if hasattr(bpy.types.Material, "volume_hist_vmax"):
            del bpy.types.Material.volume_hist_vmax
        if hasattr(bpy.types.Material, "volume_hist_vmin"):
            del bpy.types.Material.volume_hist_vmin
        if hasattr(bpy.types.Material, "volume_colormap_reversed"):
            del bpy.types.Material.volume_colormap_reversed
        if hasattr(bpy.types.Material, "volume_colormap"):
            del bpy.types.Material.volume_colormap
