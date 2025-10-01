import bpy  # type: ignore


class Annotations_Panel_3DV(bpy.types.Panel):
    bl_label = "Annotations"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendET"

    def draw(self, context):
        layout = self.layout
        props = context.scene.blend_et_annotations

        pass
