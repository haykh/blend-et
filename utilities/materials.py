import bpy
from typing import Callable


from ..colormaps.data import (
    Resolve_cmap_id,
    Stops_for_colormap,
    Apply_stops_to_colorramp,
    Enum_colormap_items,
)


class CommonMaterial_Props:
    @staticmethod
    def register(category: str, on_material_change: Callable | None = None):
        if hasattr(bpy.types.Material, f"{category}_colormap"):
            delattr(bpy.types.Material, f"{category}_colormap")
        if hasattr(bpy.types.Material, f"{category}_colormap_reversed"):
            delattr(bpy.types.Material, f"{category}_colormap_reversed")
        setattr(
            bpy.types.Material,
            f"{category}_colormap",
            bpy.props.EnumProperty(
                name="Colormap",
                description=f"Colormap for the {category} material",
                items=Enum_colormap_items,
                default=0,
                update=on_material_change,
            ),
        )
        setattr(
            bpy.types.Material,
            f"{category}_colormap_reversed",
            bpy.props.BoolProperty(
                name="Reverse colormap",
                description="Reverse the selected colormap (like Matplotlib _r)",
                default=False,
                update=on_material_change,
            ),
        )

    @staticmethod
    def unregister(category: str):
        if hasattr(bpy.types.Material, f"{category}_colormap_reversed"):
            delattr(bpy.types.Material, f"{category}_colormap_reversed")
        if hasattr(bpy.types.Material, f"{category}_colormap"):
            delattr(bpy.types.Material, f"{category}_colormap")


def CommonMaterialUI(
    category: str, layout: bpy.types.UILayout, mat: bpy.types.Material
):
    layout.row().operator(
        f"blend_et.materials_create_or_reset_{category}_material",
        icon="NODETREE",
        text=f"Create/reset {category} material",
    )
    layout.separator()

    box = layout.box()
    box.row().label(text="Colormap", icon="COLOR")
    box.row().template_icon_view(mat, f"{category}_colormap", show_labels=True, scale=5)

    box.row().operator(
        f"blend_et.materials_reverse_{category}_colormap",
        icon="ARROW_LEFTRIGHT",
        text="Reverse colormap",
    )


def CommonMaterialColormapChange(
    cmap_attr,
    cmap_reversed_attr: bool,
    name: str,
    create_or_reset_callback: Callable,
    nt: bpy.types.NodeTree,
):
    ramp_node = nt.nodes.get("Colormap")
    if ramp_node is None or ramp_node.type != "VALTORGB":
        create_or_reset_callback(name)
        ramp_node = nt.nodes.get("Colormap")
    if ramp_node:
        cm_id = Resolve_cmap_id(cmap_attr)
        rev = cmap_reversed_attr
        stops = Stops_for_colormap(cm_id, reverse=rev)
        Apply_stops_to_colorramp(ramp_node.color_ramp, stops)
    return None


def CommonMaterialReverseColormap(
    category: str,
    on_colormap_change_callback: Callable,
    ctx: bpy.types.Context,
):
    mat = getattr(ctx.object, "active_material", None)
    if mat is None:
        raise ValueError("No active material on the selected object.")
    setattr(
        mat,
        f"{category}_colormap_reversed",
        not bool(getattr(mat, f"{category}_colormap_reversed", False)),
    )
    on_colormap_change_callback(mat, ctx)
