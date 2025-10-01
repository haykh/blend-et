import bpy  # type: ignore


class Tools_Props(bpy.types.PropertyGroup):
    background_color: bpy.props.FloatVectorProperty(
        name="Background color",
        description="Background color for the scene",
        subtype="COLOR",
        default=(0.0, 0.0, 0.0),
        min=0.0,
        max=1.0,
        size=3,
    )
