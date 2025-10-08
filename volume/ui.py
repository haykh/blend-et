import bpy


class VolumeMaterial_Panel_NDE(bpy.types.Panel):
    bl_label = "Volume material"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "BlendET"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        obj = context.object
        return (
            space is not None
            and getattr(space, "tree_type", "") == "ShaderNodeTree"
            and obj is not None
            and obj.active_material is not None
        )

    def draw(self, context: bpy.types.Context):
        if (layout := self.layout) is None:
            return
        if (obj := context.object) is None or obj.active_material is None:
            return
        mat = obj.active_material

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.row().operator(
            "blend_et.materials_create_or_reset_volume_material",
            icon="NODETREE",
            text="Create/reset volume material",
        )
        layout.separator()

        box = layout.box()
        box.row().label(text="Colormap", icon="COLOR")
        box.row().template_icon_view(mat, "volume_colormap", show_labels=True, scale=5)

        box.row().operator(
            "blend_et.materials_reverse_volume_colormap",
            icon="ARROW_LEFTRIGHT",
            text="Reverse colormap",
        )

        if getattr(mat, "volume_hist_ready", False) and mat.volume_hist_image:
            layout.separator()
            box = layout.box()
            box.row().label(text="Value ranges", icon="UV_DATA")

            split = box.split()
            col = split.column(align=True)
            col.row().label(text="min/max")
            col.row().label(text=f"min: {mat.volume_hist_vmin:.3g}")
            col.row().label(text=f"max: {mat.volume_hist_vmax:.3g}")
            col = split.column(align=True)
            col.row().label(text="5% quantiles")
            col.row().label(text=f"min: {mat.volume_hist_q05:.3g}")
            col.row().label(text=f"max: {mat.volume_hist_q95:.3g}")

            box.row().label(text="Histogram", icon="GRAPH")
            row = box.row()
            row.ui_units_x = 24
            row.scale_x = 10
            row.scale_y = 10
            icon_id = mat.volume_hist_image.preview.icon_id
            row.template_icon(icon_value=icon_id)
            box.row().label(text="Quantiles shown with red lines", icon="INFO")


class Volume_Panel_3DV(bpy.types.Panel):
    bl_label = "Volume Rendering"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendET"

    def draw(self, context):
        if (layout := self.layout) is None or (scene := context.scene) is None:
            return
        props = scene.blend_et_volume_render

        layout.prop(props, "save_relative")

        layout.separator()

        box = layout.box()
        box.row().label(text="VDB → Volume (.vdb)")
        box.row().prop(props, "vdb_path")
        box.row().operator("blend_et.volume_render_import_vdb", icon="IMPORT")

        layout.separator()
        box = layout.box()
        box.row().label(text="NumPy → Volume (.npy / .npz)")
        box.row().prop(props, "numpy_path")
        box.row().prop(props, "npz_key")
        box.row().prop(props, "numpy_axis_order")
        box_crop = box.box()
        box_crop.label(text="Crop indices")
        row = box_crop.row()
        split = row.split()
        split.column().prop(props, "numpy_crop_xmin")
        split.column().prop(props, "numpy_crop_xmax")
        row = box_crop.row()
        split = row.split()
        split.column().prop(props, "numpy_crop_ymin")
        split.column().prop(props, "numpy_crop_ymax")
        row = box_crop.row()
        split = row.split()
        split.column().prop(props, "numpy_crop_zmin")
        split.column().prop(props, "numpy_crop_zmax")
        box.row().operator("blend_et.volume_render_import_numpy", icon="IMPORT")
