import bpy

import numpy as np

from ..colormaps.data import (  # pyright: ignore[reportMissingImports]
    Resolve_cmap_id,
    Stops_for_colormap,
    Apply_stops_to_colorramp,
)


def Create_or_reset_volume_material(name) -> bpy.types.Material:
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        if (nt := mat.node_tree) is None:
            raise RuntimeError("Failed to create node tree for new material")
        nt.nodes.clear()
    else:
        if not mat.use_nodes:
            mat.use_nodes = True

    if (nt := mat.node_tree) is None:
        raise RuntimeError("Failed to access node tree of material")
    nodes = nt.nodes
    links = nt.links

    def _get_or_new(nodes, type_id, name=None, label=None):
        n = nodes.get(name) if name else None
        if n is None:
            n = nodes.new(type_id)
            if name:
                n.name = name
            if label:
                n.label = label
        return n

    vol_info = _get_or_new(nodes, "ShaderNodeVolumeInfo", "VolumeInfo", "Volume info")
    vol_info.location = (-50, -100)

    map_range = _get_or_new(nodes, "ShaderNodeMapRange", "ValueRemap", "Remap values")
    map_range.location = (150, 0)

    color_ramp = _get_or_new(nodes, "ShaderNodeValToRGB", "Colormap", "Colormap")
    color_ramp.location = (400, 300)

    float_curve = _get_or_new(
        nodes, "ShaderNodeFloatCurve", "OpacityCurve", "Opacity curve"
    )
    float_curve.location = (400, 0)

    multiply_1 = _get_or_new(
        nodes, "ShaderNodeMath", "MultiplyEmissivity", "Emissivity multiplier"
    )
    multiply_1.location = (400, -400)
    multiply_1.operation = "MULTIPLY"
    multiply_1.inputs[1].default_value = 2.0

    multiply_2 = _get_or_new(
        nodes, "ShaderNodeMath", "MultiplyOpacity", "Opacity multiplier"
    )
    multiply_2.location = (800, 0)
    multiply_2.operation = "MULTIPLY"
    multiply_2.inputs[1].default_value = 1.0

    vol = _get_or_new(nodes, "ShaderNodeVolumePrincipled", "Volume", "Volume shader")
    vol.location = (1100, 100)

    out = _get_or_new(
        nodes, "ShaderNodeOutputMaterial", "MaterialOutput", "Material Output"
    )
    out.location = (1400, 100)

    def _link_if_missing(a, b):
        if not b.links or all(l.from_socket is not a for l in b.links):
            links.new(a, b)

    _link_if_missing(vol_info.outputs["Density"], map_range.inputs["Value"])
    _link_if_missing(map_range.outputs["Result"], color_ramp.inputs["Fac"])
    _link_if_missing(map_range.outputs["Result"], float_curve.inputs["Value"])
    _link_if_missing(map_range.outputs["Result"], multiply_1.inputs[0])
    _link_if_missing(float_curve.outputs["Value"], multiply_2.inputs[0])
    _link_if_missing(color_ramp.outputs["Color"], vol.inputs["Color"])
    _link_if_missing(color_ramp.outputs["Color"], vol.inputs["Emission Color"])
    _link_if_missing(multiply_1.outputs["Value"], vol.inputs["Emission Strength"])
    _link_if_missing(multiply_2.outputs["Value"], vol.inputs["Density"])
    _link_if_missing(vol.outputs["Volume"], out.inputs["Volume"])

    cm_id = Resolve_cmap_id(getattr(mat, "volume_colormap", 0))
    rev = bool(getattr(mat, "volume_colormap_reversed", False))
    Apply_stops_to_colorramp(
        color_ramp.color_ramp, Stops_for_colormap(cm_id, reverse=rev)
    )

    return mat


def Store_histogram_on_material(
    mat: bpy.types.Material,
    hist: np.ndarray,
    vmin: float,
    vmax: float,
    q05: float,
    q95: float,
    width: int = 256,
    height: int = 256,
):
    bins = int(hist.size)
    # --- draw pixels ---
    px = np.empty((height, width, 4), dtype=np.float32)

    px[..., 0:3] = 0.22
    px[..., 3] = 1.0

    hmax = int(hist.max()) if hist.size else 1
    if hmax < 1:
        hmax = 1

    # normalized heights (0..H-10)
    heights = np.ceil((hist.astype(np.float32) / float(hmax)) * (height - 10)).astype(
        np.int32
    )

    # draw per-bin rectangles with >=2 px width
    for i in range(bins):
        x0 = int(i * width / bins)
        x1 = int((i + 1) * width / bins)
        if x1 <= x0:
            x1 = x0 + 1
        # ensure visible min width
        if x1 - x0 < 2:
            x1 = x0 + 2 if x0 + 2 <= width else width

        h = int(heights[i])
        if h > 0:
            px[0:h, x0:x1, 0:3] = 0.98
            px[0:h, x0:x1, 3] = 1.0

    if vmin < q05 < vmax:
        iq05 = int((q05 - vmin) / (vmax - vmin) * width)
        px[:, iq05 : min(iq05 + 2, width), 0] = 1.0
        px[:, iq05 : min(iq05 + 2, width), 1:3] = 0.2
        px[:, iq05 : min(iq05 + 2, width), 3] = 1.0

    if vmin < q95 < vmax:
        iq95 = int((q95 - vmin) / (vmax - vmin) * width)
        px[:, iq95 : min(iq95 + 2, width), 0] = 1.0
        px[:, iq95 : min(iq95 + 2, width), 1:3] = 0.2
        px[:, iq95 : min(iq95 + 2, width), 3] = 1.0

    img_name = f"SB_Hist_{mat.name}"
    img = bpy.data.images.get(img_name)
    if img is None:
        img = bpy.data.images.new(
            img_name, width=width, height=height, alpha=True, float_buffer=True
        )
        if (img_col_settings := img.colorspace_settings) is None:
            raise RuntimeError("Failed to access color space settings of new image")
        img_col_settings.name = "Non-Color"
        img.alpha_mode = "STRAIGHT"
        img.use_fake_user = True
    else:
        if img.size[0] != width or img.size[1] != height:
            img.scale(width, height)

    img.pixels[:] = px.ravel().tolist()  # pyright: ignore[reportIndexIssue]
    img.update()
    img.preview_ensure()

    # Store on the material
    mat.volume_hist_vmin = float(vmin)
    mat.volume_hist_vmax = float(vmax)
    mat.volume_hist_q05 = float(q05)
    mat.volume_hist_q95 = float(q95)
    mat.volume_hist_image = img
    mat.volume_hist_ready = True


def Clear_histogram_on_material(mat: bpy.types.Material):
    mat.volume_hist_vmin = 0.0
    mat.volume_hist_vmax = 0.0
    mat.volume_hist_q05 = 0.0
    mat.volume_hist_q95 = 0.0
    mat.volume_hist_image = None
    mat.volume_hist_ready = False


def Create_volume_object(context, store_path, abspath, uuid_str):
    scene = context.scene
    display_name = bpy.path.display_name_from_filepath(abspath)
    base_name = f"{display_name}_Volume_{uuid_str}"

    vol_data = bpy.data.volumes.new(name=base_name)
    vol_data.filepath = store_path

    vol_obj = bpy.data.objects.new(base_name, vol_data)
    collection = context.collection or context.scene.collection
    collection.objects.link(vol_obj)
    vol_obj.location = scene.cursor.location
    vol_obj.scale = (0.01, 0.01, 0.01)

    active_obj = vol_obj
    bpy.ops.object.select_all(action="DESELECT")
    active_obj.select_set(True)
    context.view_layer.objects.active = active_obj

    mat = Create_or_reset_volume_material(f"{display_name}_Material_{uuid_str}")
    if (obj_data := vol_obj.data) is None:
        raise RuntimeError("Failed to access volume data of new object")

    if len(obj_data.materials) == 0:
        obj_data.materials.append(mat)
    else:
        obj_data.materials[0] = mat

    return base_name, display_name, mat


def On_material_colormap_change(self, context):
    """Update callback: self is the Material that owns 'volume_colormap'."""
    if not getattr(self, "use_nodes", False) or not self.node_tree:
        return None
    nt = self.node_tree
    ramp_node = nt.nodes.get("Colormap")
    if ramp_node is None or ramp_node.type != "VALTORGB":
        Create_or_reset_volume_material(self.name)
        ramp_node = nt.nodes.get("Colormap")
    if ramp_node:
        cm_id = Resolve_cmap_id(getattr(self, "volume_colormap", 0))
        rev = bool(getattr(self, "volume_colormap_reversed", False))
        stops = Stops_for_colormap(cm_id, reverse=rev)
        Apply_stops_to_colorramp(ramp_node.color_ramp, stops)
    return None
