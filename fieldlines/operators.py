import bpy

from .utils import (
    Create_raw_data_fieldline,
    Create_or_reset_fieldline_material,
    Create_fieldline_geometry,
    # Create_fieldline_mesh,
    # Create_fieldline_geometry_node,
    # Create_fieldline_controller,
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

        # bpy.ops.collection.create(name=f"Fieldlines_{uuid_str}")
        # collection = bpy.data.collections[f"Fieldlines_{uuid_str}"]
        # scene.collection.children.link(collection)

        material = Create_or_reset_fieldline_material(f"FieldlinesMaterial_{uuid_str}")

        # identify keys:
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

        seed_ys = np.linspace(0.5, sy - 0.5, 10)
        seed_zs = np.linspace(0.5, sz - 0.5, 10)
        seed_ys, seed_zs = np.meshgrid(seed_ys, seed_zs, indexing="ij")
        seed_points = np.vstack(
            [np.full(seed_ys.size, 0.5), seed_ys.ravel(), seed_zs.ravel()]
        ).T
        nfieldlines = seed_points.shape[0]

        # seed_points = np.column_stack([seed_ys.ravel(), seed_zs.ravel()])

        # nfieldlines = 5
        for i in range(nfieldlines):
            xline, yline, zline, magline = (
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
            )
            ds = 0.25
            MAXITER = 2000

            # for sign in [-1]:
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
                x += (ds * fx) / norm
                y += (ds * fy) / norm
                z += (ds * fz) / norm
                xl = np.append(xl, x)
                yl = np.append(yl, y)
                zl = np.append(zl, z)
                magl = np.append(magl, norm)
                iter += 1

                # if sign == -1:
                #     xline = xl.copy()
                #     yline = yl.copy()
                #     zline = zl.copy()
                #     magline = magl.copy()
                # else:
                #     xline = np.concatenate((xl[::-1], xline))
                #     yline = np.concatenate((yl[::-1], yline))
                #     zline = np.concatenate((zl[::-1], zline))
                #     magline = np.concatenate((magl[::-1], magline))

            # if len(xline) < 2:
            #     continue
            # npoints = 100
            # zs = np.linspace(0, 10, npoints)
            # rs = np.linspace(0, 100, npoints) ** 0.5

            # phis = np.linspace(0, 6 * np.pi, npoints)

            # xs = rs * np.sin(phis) + 5 * i
            # ys = rs * np.cos(phis)

            # ts = 1 + 0.5 * np.sin(5 * phis)

            Create_raw_data_fieldline(
                {
                    "x": xl,
                    "y": yl,
                    "z": zl,
                    "color": magl / maxnorm,
                    "thickness": magl / maxnorm,
                },
                context,
                raw_collection,
                i,
            )
            # mesh, _ = Create_fieldline_mesh(context, collection, i)
            # obj.parent = mesh
            # mesh.scale = (0.01, 0.01, 0.01)
            # Create_fieldline_geometry_node(mesh, obj, material, context)

            # if mesh.data is not None:
            #     if len(mesh.data.materials) == 0:
            #         mesh.data.materials.append(material)
            #     else:
            #         mesh.data.materials[0] = material

        Create_fieldline_geometry(context, raw_collection, uuid_str)
        # Create_fieldline_controller(collection)

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
