import bpy


class Tools_SwitchToCycles(bpy.types.Operator):
    bl_idname = "blend_et.switch_to_cycles"
    bl_label = "Switch to Cycles"
    bl_description = "Switch render engine to Cycles"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context):
        if (scene := context.scene) is None:
            self.report({"ERROR"}, "No active scene found")
            return {"CANCELLED"}
        scene.render.engine = "CYCLES"
        if (
            (prefs := bpy.context.preferences) is None
            or (addons := prefs.addons) is None
            or (cycles := addons.get("cycles")) is None
            or (cycles_prefs := cycles.preferences) is None
        ):
            self.report({"WARNING"}, "Could not access user preferences")
            return {"FINISHED"}
        if scene.cycles is None:
            self.report({"WARNING"}, "Could not access Cycles preferences")
            return {"FINISHED"}
        if cycles_prefs.compute_device_type != "NONE":
            scene.cycles.device = "GPU"
        return {"FINISHED"}


class Tools_FixColors(bpy.types.Operator):
    bl_idname = "blend_et.fix_colors"
    bl_label = "Fix Colors"
    bl_description = "Fix color management settings for scientific visualization"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context):
        if (scene := context.scene) is None:
            self.report({"ERROR"}, "No active scene found")
            return {"CANCELLED"}
        if (view_settings := scene.view_settings) is None:
            self.report({"ERROR"}, "Failed to access scene view settings")
            return {"CANCELLED"}
        view_settings.view_transform = "Standard"
        return {"FINISHED"}


class Tools_SetBackground(bpy.types.Operator):
    bl_idname = "blend_et.tools_set_background"
    bl_label = "Set Background Color"
    bl_description = "Set background color for the scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context):
        if (scene := context.scene) is None:
            self.report({"ERROR"}, "No active scene found")
            return {"CANCELLED"}
        props = scene.blend_et_tools
        color = props.background_color
        world = scene.world

        if world is None:
            world = bpy.data.worlds.new("World")
            scene.world = world

        if (node_tree := world.node_tree) is None:
            self.report({"ERROR"}, "Failed to access world node tree")
            return {"CANCELLED"}

        world.use_nodes = True
        bg_node = node_tree.nodes.get("Background")
        if bg_node is not None:
            bg_node.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
        return {"FINISHED"}
