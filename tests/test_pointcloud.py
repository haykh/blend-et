from __future__ import annotations

import bpy
import numpy as np

from .common import BlenderIntegrationTest


class PointcloudTests(BlenderIntegrationTest):
    def _assert_pointcloud(self, suffix):
        obj = bpy.data.objects.get(f"PointcloudGeometry_{suffix}")
        self.assertIsNotNone(obj)
        nodes = self.geometry_node_group(obj).nodes
        self.assertIn("PointsToVolume", nodes)
        points_to_volume = nodes["PointsToVolume"]
        # Blender >=5.0 exposes the resolution mode as an input socket; 4.5 keeps
        # it as the ``resolution_mode`` node property.
        if "Resolution Mode" in points_to_volume.inputs:
            self.assertEqual(
                "Amount", points_to_volume.inputs["Resolution Mode"].default_value
            )
        else:
            self.assertEqual("VOXEL_AMOUNT", points_to_volume.resolution_mode)
        self.assertEqual("pointcloud_volume", obj.active_material.get("category"))

    def test_npz_pointcloud(self):
        t = np.linspace(0.0, 1.0, 12, dtype=np.float32)
        path = self.workdir / "points.npz"
        np.savez(path, x=t, y=t**2, z=np.sin(t), temperature=1.0 - t)
        bpy.context.scene.blend_et_pointcloud.pointcloud_path = str(path)

        self.assert_operator_finished(bpy.ops.blend_et.pointcloud_create())
        self._assert_pointcloud("0000")
        raw = bpy.data.objects.get("PointcloudRawObj0000")
        attribute_names = set(raw.data.attributes.keys())
        self.assertTrue(
            {"x", "y", "z", "temperature"}.issubset(attribute_names),
            f"Unexpected point attributes: {sorted(attribute_names)}",
        )

    def test_csv_pointcloud(self):
        path = self.workdir / "points.csv"
        rows = np.column_stack(
            [
                np.linspace(0, 1, 8),
                np.linspace(1, 2, 8),
                np.linspace(2, 3, 8),
                np.linspace(3, 4, 8),
            ]
        )
        np.savetxt(path, rows, delimiter=",", header="x,y,z,intensity", comments="")
        bpy.context.scene.blend_et_pointcloud.pointcloud_path = str(path)

        self.assert_operator_finished(bpy.ops.blend_et.pointcloud_create())
        self._assert_pointcloud("0000")
