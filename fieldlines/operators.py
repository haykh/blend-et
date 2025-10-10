import bpy

from .utils import (
    Create_raw_data_fieldline,
    Create_or_reset_fieldline_material,
    Create_fieldline_geometry,
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

        material = Create_or_reset_fieldline_material(f"FieldlinesMaterial_{uuid_str}")

        npz_data = np.load(props.npz_path)
        fx_str, fy_str, fz_str = None, None, None
        for k in npz_data.keys():
            if len(k) >= 2 and k[-1].lower() == "x":
                fx_str = k
            elif len(k) >= 2 and k[-1].lower() == "y":
                fy_str = k
            elif len(k) >= 2 and k[-1].lower() == "z":
                fz_str = k

        if fx_str is None or fy_str is None or fz_str is None:
            self.report({"ERROR"}, "Could not identify x, y, z keys in the .npz file")
            return {"CANCELLED"}
        fx_data = npz_data[fx_str]
        fy_data = npz_data[fy_str]
        fz_data = npz_data[fz_str]
        sz, sy, sx = fx_data.shape
        if fy_data.shape != (sz, sy, sx) or fz_data.shape != (sz, sy, sx):
            self.report({"ERROR"}, "x, y, z data have different shapes")
            return {"CANCELLED"}

        maxnorm = np.sqrt(np.max(fx_data**2 + fy_data**2 + fz_data**2))

        if props.seed_points == "XY":
            seed_xs = np.linspace(0.5, sx - 0.5, props.seed_resolution[0])
            seed_ys = np.linspace(0.5, sy - 0.5, props.seed_resolution[1])
            seed_xs, seed_ys = np.meshgrid(seed_xs, seed_ys, indexing="ij")
            seed_zs = np.full(seed_xs.size, props.seed_displacement)
        elif props.seed_points == "XZ":
            seed_xs = np.linspace(0.5, sx - 0.5, props.seed_resolution[0])
            seed_zs = np.linspace(0.5, sz - 0.5, props.seed_resolution[1])
            seed_xs, seed_zs = np.meshgrid(seed_xs, seed_zs, indexing="ij")
            seed_ys = np.full(seed_xs.size, props.seed_displacement)
        elif props.seed_points == "YZ":
            seed_ys = np.linspace(0.5, sy - 0.5, props.seed_resolution[0])
            seed_zs = np.linspace(0.5, sz - 0.5, props.seed_resolution[1])
            seed_ys, seed_zs = np.meshgrid(seed_ys, seed_zs, indexing="ij")
            seed_xs = np.full(seed_ys.size, props.seed_displacement)
        elif props.seed_points == "Custom":
            self.report({"ERROR"}, "Custom seed points not implemented yet")
            return {"CANCELLED"}
        else:
            self.report({"ERROR"}, "Invalid seed points option")
            return {"CANCELLED"}

        seed_points = np.vstack([seed_xs.ravel(), seed_ys.ravel(), seed_zs.ravel()]).T

        nfieldlines = seed_points.shape[0]

        for i in range(nfieldlines):
            xline, yline, zline, magline = (
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
            )
            ds = props.integration_step
            MAXITER = props.integration_maxiter
            if props.integration_direction == "Plus":
                signs = [+1]
            elif props.integration_direction == "Minus":
                signs = [-1]
            else:  # Both
                signs = [+1, -1]

            for sign in signs:
                xl, yl, zl, magl = (
                    np.array([]),
                    np.array([]),
                    np.array([]),
                    np.array([]),
                )
                x, y, z = seed_points[i, :]
                iter = 0
                while iter < MAXITER and (
                    0 <= x < sx - 1 and 0 <= y < sy - 1 and 0 <= z < sz - 1
                ):
                    ix, iy, iz = int(x), int(y), int(z)
                    fx = fx_data[iz, iy, ix]
                    fy = fy_data[iz, iy, ix]
                    fz = fz_data[iz, iy, ix]
                    norm = (fx**2 + fy**2 + fz**2) ** 0.5
                    if norm < 1e-8:
                        break
                    x += sign * (ds * fx) / norm
                    y += sign * (ds * fy) / norm
                    z += sign * (ds * fz) / norm
                    xl = np.append(xl, x)
                    yl = np.append(yl, y)
                    zl = np.append(zl, z)
                    magl = np.append(magl, norm)
                    iter += 1

                if sign == +1:
                    xline = np.append(xl[::-1], xline)
                    yline = np.append(yl[::-1], yline)
                    zline = np.append(zl[::-1], zline)
                    magline = np.append(magl[::-1], magline)
                else:
                    xline = np.append(xline, xl)
                    yline = np.append(yline, yl)
                    zline = np.append(zline, zl)
                    magline = np.append(magline, magl)

            Create_raw_data_fieldline(
                {
                    "x": xline,
                    "y": yline,
                    "z": zline,
                    "color": magline / maxnorm,
                    "thickness": magline / maxnorm,
                },
                context,
                raw_collection,
                i,
            )

        mesh = Create_fieldline_geometry(context, raw_collection, material, uuid_str)
        mesh.active_material = material
        mesh.scale = (0.01, 0.01, 0.01)

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
