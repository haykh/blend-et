import bpy

from .utils import (
    Create_raw_data_fieldline,
    Create_or_reset_fieldline_material,
    Create_fieldline_mesh,
    Create_fieldline_geometry_node,
    Create_fieldline_controller,
    On_material_colormap_change,
)


class Fieldlines_Create(bpy.types.Operator):
    bl_idname = "blend_et.fieldlines_create"
    bl_label = "Create Fieldlines from NumPy file"
    bl_description = "Create a new fieldline object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context):
        if (scene := context.scene) is None:
            self.report({"ERROR"}, "No active scene found")
            return {"CANCELLED"}

        import numpy as np

        props = scene.blend_et_fieldlines
        uuid_str = f"{props.uuid:04d}"
        props.uuid += 1

        bpy.ops.collection.create(name=f"FieldlinesRaw_{uuid_str}")
        raw_collection = bpy.data.collections[f"FieldlinesRaw_{uuid_str}"]
        raw_collection.hide_viewport = True
        raw_collection.hide_render = True
        raw_collection.hide_select = True
        scene.collection.children.link(raw_collection)

        bpy.ops.collection.create(name=f"Fieldlines_{uuid_str}")
        collection = bpy.data.collections[f"Fieldlines_{uuid_str}"]
        scene.collection.children.link(collection)

        material = Create_or_reset_fieldline_material(f"FieldlinesMaterial_{uuid_str}")

        nfieldlines = 5
        for i in range(nfieldlines):
            npoints = 100
            zs = np.linspace(0, 10, npoints)
            rs = np.linspace(0, 100, npoints) ** 0.5

            phis = np.linspace(0, 6 * np.pi, npoints)

            xs = rs * np.sin(phis) + 5 * i
            ys = rs * np.cos(phis)

            ts = 1 + 0.5 * np.sin(5 * phis)
            obj, _ = Create_raw_data_fieldline(
                {"x": xs, "y": ys, "z": zs, "mag": ts}, context, raw_collection, i
            )
            mesh, _ = Create_fieldline_mesh(context, collection, i)
            obj.parent = mesh
            Create_fieldline_geometry_node(mesh, obj, material, context)

            if mesh.data is not None:
                if len(mesh.data.materials) == 0:
                    mesh.data.materials.append(material)
                else:
                    mesh.data.materials[0] = material

        Create_fieldline_controller(collection)

        return {"FINISHED"}


class FieldlineMaterial_ReverseColormap(bpy.types.Operator):
    bl_idname = "blend_et.materials_reverse_fieldline_colormap"
    bl_label = "Reverse colormap"
    bl_description = "Reverse the active material's colormap"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context):
        mat = getattr(context.object, "active_material", None)
        if mat is None:
            self.report({"ERROR"}, "No active material on the selected object.")
            return {"CANCELLED"}
        mat.fieldline_colormap_reversed = not bool(
            getattr(mat, "fieldline_colormap_reversed", False)
        )
        On_material_colormap_change(mat, context)
        self.report({"INFO"}, f"Colormap reversed: {mat.fieldline_colormap_reversed}")
        return {"FINISHED"}


class FieldlineMaterial_CreateOrReset(bpy.types.Operator):
    bl_idname = "blend_et.materials_create_or_reset_fieldline_material"
    bl_label = "Create or Reset Fieldline Material"
    bl_description = (
        "Create a basic material for the fieldlines rendering or reset the existing one"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context):
        mat = getattr(context.object, "active_material", None)
        if mat is None:
            self.report({"ERROR"}, "No active material on the selected object.")
            return {"CANCELLED"}
        Create_or_reset_fieldline_material(mat.name)
        self.report({"INFO"}, f"Fieldline material nodes ready on '{mat.name}'.")
        return {"FINISHED"}
