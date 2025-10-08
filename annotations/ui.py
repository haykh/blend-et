import bpy


class Annotations_Panel_3DV(bpy.types.Panel):
    bl_label = "Annotations"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendET"

    def draw(self, _: bpy.types.Context):
        if (layout := self.layout) is None:
            return
        layout.operator("blend_et.annotations_add_axes_grid", icon="MESH_GRID")
