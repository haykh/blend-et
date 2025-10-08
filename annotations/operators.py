import bpy

from .utils import Axes_grid_geometry_node  # type: ignore


class Annotations_AddAxesGrid(bpy.types.Operator):
    bl_idname = "blend_et.annotations_add_axes_grid"
    bl_label = "Add axes grid"
    bl_description = "Add a customizable mesh for representing the axes of the grid"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context):
        if (scene := context.scene) is None:
            self.report({"ERROR"}, "No active scene found")
            return {"CANCELLED"}
        props = scene.blend_et_annotations
        uuid_str = f"{props.uuid:04d}"
        props.uuid += 1
        bpy.ops.object.volume_add(align="WORLD")
        empty = context.active_object
        if empty is None:
            self.report({"ERROR"}, "Failed to create empty object")
            return {"CANCELLED"}
        empty.name = f"AxesGrid_{uuid_str}"
        mod = empty.modifiers.new(name="GeometryNodes", type="NODES")
        mod.node_group = Axes_grid_geometry_node()
        return {"FINISHED"}
