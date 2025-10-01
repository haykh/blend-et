import bpy  # type: ignore


class Latex_Panel_3DV(bpy.types.Panel):
    bl_label = "Latex"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendET"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        props = context.scene.blend_et_latex

        layout.label(text="Adapted from ghseeli/latex2blender", icon="INFO")
        layout.separator()

        layout.prop(props, "latex_code")
        layout.separator()

        layout.prop(props, "command_selection")
        layout.separator

        box = layout.box()
        box.label(text="Paths to directories containing commands.")
        box.label(
            text="If the plugin is unable to find the commands, set them here.",
            icon="INFO",
        )
        box.row().prop(props, "custom_latex_path")
        box.row().prop(props, "custom_pdflatex_path")
        box.row().prop(props, "custom_xelatex_path")
        box.row().prop(props, "custom_lualatex_path")
        box.row().prop(props, "custom_dvisvgm_path")

        box = layout.box()
        box.label(text="Transform Settings")
        box.row().prop(props, "text_scale")
        box.row().prop(props, "text_thickness")

        split = box.split()

        col = split.column(align=True)
        col.label(text="Location:")
        col.prop(props, "x_loc")
        col.prop(props, "y_loc")
        col.prop(props, "z_loc")

        col = split.column(align=True)
        col.label(text="Rotation:")
        col.prop(props, "x_rot")
        col.prop(props, "y_rot")
        col.prop(props, "z_rot")

        layout.prop(props, "custom_preamble_bool")
        if props.custom_preamble_bool:
            layout.prop(props, "preamble_path")

        layout.prop(props, "custom_material_bool")
        if props.custom_material_bool:
            layout.prop(props, "custom_material_value")

        layout.separator()

        box = layout.box()
        row = box.row()
        row.operator("blend_et.latex_compile_as_mesh", icon="MESH_CUBE")
        row = box.row()
        row.operator("blend_et.latex_compile_as_grease_pencil", icon="GREASEPENCIL")
