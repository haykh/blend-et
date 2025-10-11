import bpy

from .utils import Add_simple_material_to_object, Axes_grid_geometry_node, Arrow_geometry_node  # type: ignore


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
        bpy.ops.mesh.primitive_circle_add(align="WORLD")
        empty = context.active_object
        if empty is None:
            self.report({"ERROR"}, "Failed to create empty object")
            return {"CANCELLED"}
        empty.name = f"AxesGrid_{uuid_str}"

        mat = Add_simple_material_to_object(
            empty,
            f"AxesGridMaterial_{uuid_str}",
            {"Base Color": (0, 0, 0, 1), "Roughness": 0.5},
        )

        mod = empty.modifiers.new(name="GeometryNodes", type="NODES")
        mod.node_group = Axes_grid_geometry_node(mat)
        return {"FINISHED"}


class Annotations_AddArrow(bpy.types.Operator):
    bl_idname = "blend_et.annotations_add_arrow"
    bl_label = "Add arrow"
    bl_description = "Add a customizable arrow mesh"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context):
        if (scene := context.scene) is None:
            self.report({"ERROR"}, "No active scene found")
            return {"CANCELLED"}
        props = scene.blend_et_annotations
        uuid_str = f"{props.uuid:04d}"
        props.uuid += 1
        bpy.ops.mesh.primitive_circle_add(align="WORLD")
        empty = context.active_object
        if empty is None:
            self.report({"ERROR"}, "Failed to create empty object")
            return {"CANCELLED"}
        empty.name = f"Arrow_{uuid_str}"

        mat = Add_simple_material_to_object(
            empty,
            f"ArrowMaterial_{uuid_str}",
            {"Base Color": (0.05, 0.05, 0.05, 1), "Roughness": 0.5},
        )

        mod = empty.modifiers.new(name="GeometryNodes", type="NODES")
        mod.node_group = Arrow_geometry_node(mat)
        empty.modifiers.new(name="EdgeSplit", type="EDGE_SPLIT")

        return {"FINISHED"}
