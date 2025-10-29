import bpy


class Tools_Panel_3DV(bpy.types.Panel):
    bl_label = "Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendET"

    def draw(self, context: bpy.types.Context):
        if (layout := self.layout) is None or (scene := context.scene) is None:
            return
        props = scene.blend_et_tools
        box = layout.box()
        box.row().label(
            text="Enable CUDA/HIP/OneAPI support in Preferences before proceeding.",
            icon="INFO",
        )
        box.row().operator("blend_et.switch_to_cycles", icon="RENDER_STILL")
        box.row().operator("blend_et.fix_colors", icon="COLOR")
        box.row().operator("blend_et.clear_unused_data", icon="TRASH")

        layout.separator()
        box = layout.box()
        box.row().prop(props, "background_color")
        box.row().operator("blend_et.tools_set_background", icon="WORLD")
