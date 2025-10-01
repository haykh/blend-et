import bpy  # type: ignore


class Tools_SwitchToCycles(bpy.types.Operator):
    bl_idname = "blend_et.switch_to_cycles"
    bl_label = "Switch to Cycles"
    bl_description = "Switch render engine to Cycles"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.render.engine = "CYCLES"
        if (
            bpy.context.preferences.addons["cycles"].preferences.compute_device_type
            != "NONE"
        ):
            context.scene.cycles.device = "GPU"
        return {"FINISHED"}


class Tools_FixColors(bpy.types.Operator):
    bl_idname = "blend_et.fix_colors"
    bl_label = "Fix Colors"
    bl_description = "Fix color management settings for scientific visualization"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        scene.view_settings.view_transform = "Standard"
        return {"FINISHED"}


class Tools_SetBackground(bpy.types.Operator):
    bl_idname = "blend_et.tools_set_background"
    bl_label = "Set Background Color"
    bl_description = "Set background color for the scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.blend_et_tools
        color = props.background_color
        world = bpy.context.scene.world
        if world is None:
            world = bpy.data.worlds.new("World")
            bpy.context.scene.world = world
        world.use_nodes = True
        bg_node = world.node_tree.nodes.get("Background")
        if bg_node is not None:
            bg_node.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
        return {"FINISHED"}
