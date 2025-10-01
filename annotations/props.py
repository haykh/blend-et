import bpy  # type: ignore

class Annotations_Props(bpy.types.PropertyGroup):
    uuid: bpy.props.IntProperty(
        name="UUID",
        description="UUID for the annotation object",
        default=0,
    )

