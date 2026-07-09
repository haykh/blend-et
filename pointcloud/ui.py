import bpy

from ..utilities.materials import (
    CommonMaterialUI,
)


class PointcloudMaterial_Panel_NDE(bpy.types.Panel):
    bl_label = "Pointcloud material"
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
            and obj.active_material.get("category", None) == "pointcloud_volume"
        )

    def draw(self, context: bpy.types.Context):
        if (layout := self.layout) is None:
            return
        if (obj := context.object) is None or obj.active_material is None:
            return
        mat = obj.active_material

        layout.use_property_split = True
        layout.use_property_decorate = False

        CommonMaterialUI(category="pointcloud", layout=layout, mat=mat)


class Pointcloud_Panel_3DV(bpy.types.Panel):
    bl_label = "Pointcloud"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendET"

    def draw(self, context: bpy.types.Context):
        if (layout := self.layout) is None or (scene := context.scene) is None:
            return
        props = scene.blend_et_pointcloud
        layout.label(text="NumPy/CSV → Pointcloud (.npz/.csv)")
        layout.prop(props, "pointcloud_path")

        layout.separator()
        layout.row().operator("blend_et.pointcloud_create", icon="POINTCLOUD_DATA")
