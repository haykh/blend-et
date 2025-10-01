import bpy  # type: ignore

import numpy as np  # type: ignore

import os

from .utils import (
    Create_or_reset_volume_material,
    Create_volume_object,
    Store_histogram_on_material,
    Clear_histogram_on_material,
    On_material_colormap_change,
)


class VolumeMaterial_ReverseColormap(bpy.types.Operator):
    bl_idname = "blend_et.materials_reverse_volume_colormap"
    bl_label = "Reverse colormap"
    bl_description = "Reverse the active material's colormap"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        mat = getattr(context.object, "active_material", None)
        if mat is None:
            self.report({"ERROR"}, "No active material on the selected object.")
            return {"CANCELLED"}
        mat.volume_colormap_reversed = not bool(
            getattr(mat, "volume_colormap_reversed", False)
        )
        On_material_colormap_change(mat, context)
        self.report({"INFO"}, f"Colormap reversed: {mat.volume_colormap_reversed}")
        return {"FINISHED"}


class VolumeMaterial_CreateOrReset(bpy.types.Operator):
    bl_idname = "blend_et.materials_create_or_reset_volume_material"
    bl_label = "Create or Reset Volume Material"
    bl_description = (
        "Create a basic material for volume rendering or reset the existing one"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        mat = getattr(context.object, "active_material", None)
        if mat is None:
            self.report({"ERROR"}, "No active material on the selected object.")
            return {"CANCELLED"}
        Create_or_reset_volume_material(mat.name)
        self.report({"INFO"}, f"Volume material nodes ready on '{mat.name}'.")
        return {"FINISHED"}


class Volume_ImportVDB(bpy.types.Operator):
    bl_idname = "blend_et.volume_render_import_vdb"
    bl_label = "Import .vdb as volume"
    bl_description = "Import a .vdb file and create a volume object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scn = context.scene
        props = scn.blend_et_volume_render

        if not props.vdb_path:
            self.report({"ERROR"}, "Please pick a valid .vdb file first.")
            return {"CANCELLED"}

        abspath = bpy.path.abspath(props.vdb_path)
        if not os.path.exists(abspath):
            self.report({"ERROR"}, f"File not found:\n{abspath}")
            return {"CANCELLED"}

        store_path = bpy.path.relpath(abspath) if props.save_relative else abspath
        uuid_str = f"{props.uuid:04d}"
        props.uuid += 1
        _, display_name, mat = Create_volume_object(
            context, store_path, abspath, uuid_str
        )

        if mat is not None:
            Clear_histogram_on_material(mat)

        self.report({"INFO"}, f"Created Volume from .vdb file: {display_name}")
        return {"FINISHED"}


class Volume_ImportNumpy(bpy.types.Operator):
    bl_idname = "blend_et.volume_render_import_numpy"
    bl_label = "Import .npy/.npz as volume"
    bl_description = (
        "Load a 3D NumPy array (.npy/.npz) and create a Volume object via OpenVDB"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        import os

        def _compute_histogram_np(arr: np.ndarray, bins: int = 128):
            """
            Returns (hist: np.ndarray[int], q05: float, q95: float, vmin: float, vmax: float).
            Uses full range [min, max] for the histogram, and rough numpy quantiles for 5/95%.
            Assumes arr is already finite and float.
            """
            flat = arr.astype(np.float64, copy=False).ravel()
            if flat.size == 0:
                return np.zeros(bins, dtype=np.int32), 0.0, 0.0, 0.0, 1.0

            vmin = float(flat.min())
            vmax = float(flat.max())

            if vmax == vmin:
                vmax = vmin + 1e-12
            cnt, bns = np.histogram(flat, bins=bins, range=(vmin, vmax))
            bns = 0.5 * (bns[1:] + bns[:-1])
            cumsum = np.cumsum(cnt)
            imin = np.argmin(
                np.abs(cumsum - 0.05 * (cumsum[-1] - cumsum[0]) - cumsum[0])
            )
            imax = np.argmin(
                np.abs(cumsum - 0.95 * (cumsum[-1] - cumsum[0]) - cumsum[0])
            )
            q05, q95 = bns[imin], bns[imax]
            return cnt.astype(np.int32, copy=False), float(q05), float(q95), vmin, vmax

        props = context.scene.blend_et_volume_render
        path = bpy.path.abspath(props.numpy_path or "")
        if not path or not os.path.exists(path):
            self.report({"ERROR"}, "Pick a valid .npy /.npz file first.")
            return {"CANCELLED"}

        directory = os.path.dirname(path)
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".npy":
                arr = np.load(path, allow_pickle=False)
            elif ext == ".npz":
                z = np.load(path, allow_pickle=False)
                key = props.npz_key.strip()
                if not key:
                    self.report(
                        {"ERROR"}, f"NPZ datasets: {list(z.files)} — set 'NPZ field'."
                    )
                    return {"CANCELLED"}
                if key not in z.files:
                    self.report(
                        {"ERROR"}, f"'{key}' not in NPZ datasets: {list(z.files)}"
                    )
                    return {"CANCELLED"}
                arr = z[key]
            else:
                self.report({"ERROR"}, "File must be .npy or .npz")
                return {"CANCELLED"}
        except Exception as e:
            self.report({"ERROR"}, f"Failed to load array: {e}")
            return {"CANCELLED"}

        if arr.ndim == 2:
            arr = arr[None, ...]  # treat as single slice: Z=1
        if arr.ndim != 3:
            self.report({"ERROR"}, f"Array must be 3D (got shape {arr.shape})")
            return {"CANCELLED"}

        # crop
        zmin = props.numpy_crop_zmin
        zmax = props.numpy_crop_zmax
        ymin = props.numpy_crop_ymin
        ymax = props.numpy_crop_ymax
        xmin = props.numpy_crop_xmin
        xmax = props.numpy_crop_xmax
        self.report(
            {"INFO"}, f"Cropping to Z[{zmin}:{zmax}] Y[{ymin}:{ymax}] X[{xmin}:{xmax}]"
        )
        try:
            arr = arr[xmin:xmax, ymin:ymax, zmin:zmax]
        except Exception as e:
            self.report({"ERROR"}, f"Invalid crop indices: {e}")
            return {"CANCELLED"}
        if arr.size == 0:
            self.report({"ERROR"}, "Cropped array is empty.")
            return {"CANCELLED"}

        order_map = {
            "ZYX": (0, 1, 2),
            "XYZ": (2, 1, 0),
            "YZX": (1, 2, 0),
            "ZXY": (0, 2, 1),
            "XZY": (2, 0, 1),
            "YXZ": (1, 0, 2),
        }
        axes = order_map.get(props.numpy_axis_order, (0, 1, 2))
        arr = np.transpose(arr, axes).astype(np.float64, copy=False)
        arr = np.nan_to_num(arr, copy=False, nan=0.0, posinf=0.0, neginf=0.0)

        _hist, _q05, _q95, _vmin, _vmax = _compute_histogram_np(arr, bins=128)

        try:
            try:
                import pyopenvdb as vdb  # type: ignore
            except Exception:
                import openvdb as vdb  # type: ignore
        except Exception:
            self.report(
                {"ERROR"},
                "pyopenvdb is not installed in Blender's Python. "
                "Install into Blender's Python and try again.",
            )
            return {"CANCELLED"}

        grid = vdb.DoubleGrid()
        grid.name = "density"
        grid.copyFromArray(arr)

        # Output file under same directory in 'BlendET_cache'
        uuid_str = f"{props.uuid:04d}"
        props.uuid += 1
        blend_dir = (
            directory if os.path.isabs(path) else os.path.dirname(bpy.data.filepath)
        )
        cache_dir = os.path.join(blend_dir, "BlendET_cache")
        os.makedirs(cache_dir, exist_ok=True)
        if ext == ".npz":
            base = os.path.splitext(os.path.basename(path))[0]
            if props.npz_key.strip():
                base += f"_{props.npz_key.strip()}"
        else:
            base = os.path.splitext(os.path.basename(path))[0]
        vdb_path = os.path.join(cache_dir, f"{base}_{uuid_str}.vdb")
        try:
            vdb.write(vdb_path, grids=[grid])
        except Exception as e:
            self.report({"ERROR"}, f"Failed to write VDB: {e}")
            return {"CANCELLED"}

        store_path = bpy.path.relpath(vdb_path) if props.save_relative else vdb_path
        vol_name, _, mat = Create_volume_object(context, store_path, vdb_path, uuid_str)

        if mat is not None:
            Store_histogram_on_material(mat, _hist, _vmin, _vmax, _q05, _q95)

        self.report(
            {"INFO"},
            f"Imported array as Volume: {vol_name}  (VDB: {os.path.basename(vdb_path)})",
        )
        return {"FINISHED"}
