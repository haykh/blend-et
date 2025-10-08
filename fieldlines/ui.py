import bpy


class FieldlineMaterial_Panel_NDE(bpy.types.Panel):
    bl_label = "Fieldline material"
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
            "blend_et.materials_create_or_reset_fieldline_material",
            icon="NODETREE",
            text="Create/reset fieldline material",
        )
        layout.separator()

        box = layout.box()
        box.row().label(text="Colormap", icon="COLOR")
        box.row().template_icon_view(
            mat, "fieldline_colormap", show_labels=True, scale=5
        )

        box.row().operator(
            "blend_et.materials_reverse_fieldline_colormap",
            icon="ARROW_LEFTRIGHT",
            text="Reverse colormap",
        )


class Fieldlines_Panel_3DV(bpy.types.Panel):
    bl_label = "Fieldlines"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendET"

    def draw(self, context: bpy.types.Context):
        if (layout := self.layout) is None or (scene := context.scene) is None:
            return
        props = scene.blend_et_fieldlines
        layout.label(text="NumPy → Fieldlines (.npz)")
        layout.prop(props, "npz_path")
        layout.operator("blend_et.fieldlines_create", icon="CURVES")
