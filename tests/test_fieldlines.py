from __future__ import annotations

import bpy
import numpy as np

from .common import BlenderIntegrationTest


class FieldlineTests(BlenderIntegrationTest):
    def test_fieldline_generation(self):
        shape = (6, 6, 6)
        fx = np.ones(shape, dtype=np.float32)
        fy = np.full(shape, 0.2, dtype=np.float32)
        fz = np.zeros(shape, dtype=np.float32)
        path = self.workdir / "vector_field.npz"
        np.savez(path, bx=fx, by=fy, bz=fz)

        props = bpy.context.scene.blend_et_fieldlines
        props.npz_path = str(path)
        props.crop_xmin, props.crop_xmax = 0, shape[2]
        props.crop_ymin, props.crop_ymax = 0, shape[1]
        props.crop_zmin, props.crop_zmax = 0, shape[0]
        props.integration_direction = "Both"
        props.integration_step = 0.5
        props.integration_maxiter = 8
        props.seed_points = "XY"
        props.seed_resolution = (1, 1)
        props.seed_displacement = 2.0

        self.assert_operator_finished(bpy.ops.blend_et.fieldlines_create())

        result = bpy.data.objects.get("FieldlineGeometry_0000")
        self.assertIsNotNone(result)
        self.assertEqual("fieldline", result.active_material.get("category"))
        self.assertIn("GroupOutput", self.geometry_node_group(result).nodes)

        raw = bpy.data.collections.get("FieldlinesRaw_0000")
        self.assertIsNotNone(raw)
        self.assertEqual(1, len(raw.objects))
        for obj in raw.objects:
            self.assertGreater(len(obj.data.vertices), 0)
            self.assertTrue(
                {"x", "y", "z", "color", "thickness"}.issubset(
                    obj.data.attributes.keys()
                )
            )
