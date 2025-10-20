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
    field_prefix: bpy.props.StringProperty(
        name="Field prefix",
        description="Prefix used to take field components: {prefix}x, {prefix}y, {prefix}z",
    )
    integration_direction: bpy.props.EnumProperty(
        name="Integration direction",
        description="Fieldline integration direction",
        items=[
            ("Both", "Both", "Integrate in both directions"),
            ("Plus", "Plus", "Integrate in positive direction only"),
            ("Minus", "Minus", "Integrate in negative direction only"),
        ],
        default="Both",
    )
    integration_step: bpy.props.FloatProperty(
        name="Integration step",
        description="Integration step size (in units of cells)",
        default=0.5,
        precision=3,
        min=0.001,
    )
    integration_maxiter: bpy.props.IntProperty(
        name="Max iterations",
        description="Maximum number of integration iterations",
        default=1000,
        min=1,
        max=100000,
    )
    seed_points: bpy.props.EnumProperty(
        name="Seed points",
        description="Preset for seed points",
        items=[
            ("XY", "XY plane", "Along XY plane"),
            ("XZ", "XZ plane", "Along XZ plane"),
            ("YZ", "YZ plane", "Along YZ plane"),
            ("Custom", "Custom seed", "Custom seed points provided in the .npz file"),
        ],
        default="XY",
    )
    seed_resolution: bpy.props.IntVectorProperty(
        name="Seed resolution",
        description="Number of seed points along each axis",
        size=2,
        default=(10, 10),
        min=1,
        max=100,
    )
    seed_displacement: bpy.props.FloatProperty(
        name="Seed plane displacement",
        description="Displacement of the seed plane along the axis normal in cells",
        default=0.0,
        precision=3,
    )
    custom_seed_label: bpy.props.StringProperty(
        name="Custom seed label",
        description="Label for the custom seed points in the .npz file",
        default="seed_points",
    )
    crop_xmin: bpy.props.IntProperty(
        name="X min",
        description="Crop arrays: minimum X index (inclusive)",
        default=0,
    )
    crop_xmax: bpy.props.IntProperty(
        name="X max",
        description="Crop arrays: maximum X index (exclusive)",
        default=-1,
    )
    crop_ymin: bpy.props.IntProperty(
        name="Y min",
        description="Crop arrays: minimum Y index (inclusive)",
        default=0,
    )
    crop_ymax: bpy.props.IntProperty(
        name="Y max",
        description="Crop arrays: maximum Y index (exclusive)",
        default=-1,
    )
    crop_zmin: bpy.props.IntProperty(
        name="Z min",
        description="Crop arrays: minimum Z index (inclusive)",
        default=0,
    )
    crop_zmax: bpy.props.IntProperty(
        name="Z max",
        description="Crop arrays: maximum Z index (exclusive)",
        default=-1,
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
