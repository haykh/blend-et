import bpy  # type: ignore


class Annotations_AddAxesCube(bpy.types.Operator):
    bl_idname = "blend_et.annotations_add_axes_cube"
    bl_label = "Add axes grid cube"
    bl_description = "Add a customizable mesh for representing the axes of the grid"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.blend_et_annotations
        uuid_str = f"{props.uuid:04d}"
        props.uuid += 1
        return {"FINISHED"}
