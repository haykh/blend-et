import bpy

from .utils import (
    Create_pointcloud_mesh,
    Create_or_reset_pointcloud_volume_material,
    Create_or_reset_pointcloud_mesh_material,
    On_material_colormap_change,
)

from ..utilities.data import Encode_raw_data
from ..utilities.materials import (
    CommonMaterialReverseColormap,
)
from ..utilities.types import OperatorReturnItems


class Pointcloud_Create(bpy.types.Operator):
    bl_idname = "blend_et.pointcloud_create"
    bl_label = "Create Pointcloud"
    bl_description = "Create a pointcloud from the selected data file"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[OperatorReturnItems]:
        if (scene := context.scene) is None:
            self.report({"ERROR"}, "No active scene found")
            return {"CANCELLED"}
        props = scene.blend_et_pointcloud
        pointcloud_path = props.pointcloud_path
        if pointcloud_path == "":
            self.report({"ERROR"}, "No pointcloud file path specified")
            return {"CANCELLED"}

        import numpy as np

        data: dict[str, list[float] | np.ndarray] = {}
        if pointcloud_path.lower().endswith(".npz"):
            with np.load(pointcloud_path) as npz_data:
                for k in npz_data.keys():
                    data[k] = npz_data[k]
        elif pointcloud_path.lower().endswith(".csv"):
            skiprows = 0
            cols = []
            with open(pointcloud_path, "r") as f:
                first_line = f.readline()
                if not all(
                    part.replace(".", "", 1)
                    .replace("-", "", 1)
                    .replace("e", "", 1)
                    .isdigit()
                    for part in first_line.split(",")
                ):
                    skiprows = 1
                    cols = [c.strip() for c in first_line.replace("#", "").split(",")]
            data_raw = np.loadtxt(pointcloud_path, delimiter=",", skiprows=skiprows)
            if cols == []:
                cols = [
                    f"col_{i - 2}" if i >= 2 else "xyz"[i]
                    for i in range(data_raw.shape[1])
                ]
            for i, col in enumerate(cols):
                data[col] = data_raw[:, i]
        else:
            self.report({"ERROR"}, "Unsupported file format. Please use .npz or .csv")
            return {"CANCELLED"}

        props = scene.blend_et_pointcloud
        uuid_str = f"{props.uuid:04d}"
        props.uuid += 1

        raw_collection_name = "PointcloudRaw"
        raw_collection = bpy.data.collections.get(raw_collection_name)
        if raw_collection is None:
            raw_collection = bpy.data.collections.new(raw_collection_name)
            scene.collection.children.link(raw_collection)

        raw_collection.hide_viewport = True
        raw_collection.hide_render = True
        raw_collection.hide_select = True

        material_volume = Create_or_reset_pointcloud_volume_material(
            f"PointcloudVolumeMaterial_{uuid_str}"
        )
        material_mesh = Create_or_reset_pointcloud_mesh_material(
            f"PointcloudMeshMaterial_{uuid_str}"
        )

        raw_obj, _ = Encode_raw_data(
            data, context, raw_collection, "Pointcloud", uuid_str
        )

        mesh = Create_pointcloud_mesh(
            context, raw_obj, material_volume, material_mesh, uuid_str
        )
        mesh.active_material = material_volume

        return {"FINISHED"}


class PointcloudMaterial_ReverseColormap(bpy.types.Operator):
    bl_idname = "blend_et.materials_reverse_pointcloud_colormap"
    bl_label = "Reverse colormap"
    bl_description = "Reverse the active material's colormap"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[OperatorReturnItems]:
        try:
            CommonMaterialReverseColormap(
                category="pointcloud",
                on_colormap_change_callback=On_material_colormap_change,
                ctx=context,
            )
            self.report({"INFO"}, "Colormap reversed")
            return {"FINISHED"}
        except Exception as e:
            self.report({"ERROR"}, f"Failed to reverse colormap: {e}")
            return {"CANCELLED"}


class PointcloudMaterial_CreateOrReset(bpy.types.Operator):
    bl_idname = "blend_et.materials_create_or_reset_pointcloud_material"
    bl_label = "Create or Reset Pointcloud Material"
    bl_description = (
        "Create a basic material for the pointcloud rendering or reset the existing one"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[OperatorReturnItems]:
        mat = getattr(context.object, "active_material", None)
        if mat is None:
            self.report({"ERROR"}, "No active material on the selected object.")
            return {"CANCELLED"}
        Create_or_reset_pointcloud_volume_material(mat.name)
        self.report({"INFO"}, f"Pointcloud material nodes ready on '{mat.name}'.")
        return {"FINISHED"}
