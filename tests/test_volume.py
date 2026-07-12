from __future__ import annotations

from pathlib import Path

import bpy
import numpy as np

from .common import BlenderIntegrationTest


class VolumeTests(BlenderIntegrationTest):
    def _configure_crop(self, shape):
        props = bpy.context.scene.blend_et_volume_render
        props.numpy_crop_xmin = 0
        props.numpy_crop_xmax = shape[0]
        props.numpy_crop_ymin = 0
        props.numpy_crop_ymax = shape[1]
        props.numpy_crop_zmin = 0
        props.numpy_crop_zmax = shape[2]

    def test_numpy_and_vdb_import(self):
        data = self.gaussian_volume()
        npy_path = self.workdir / "density.npy"
        np.save(npy_path, data)

        props = bpy.context.scene.blend_et_volume_render
        props.numpy_path = str(npy_path)
        props.numpy_axis_order = "ZYX"
        props.save_relative = False
        self._configure_crop(data.shape)

        self.assert_operator_finished(bpy.ops.blend_et.volume_render_import_numpy())
        volumes = [obj for obj in bpy.data.objects if obj.type == "VOLUME"]
        self.assertEqual(1, len(volumes))
        volume = volumes[0]
        self.assertEqual("volume", volume.active_material.get("category"))
        self.assertTrue(volume.active_material.volume_hist_ready)
        self.assertIn("VolumeShader", volume.active_material.node_tree.nodes)

        generated_vdb = Path(bpy.path.abspath(volume.data.filepath))
        self.assertTrue(generated_vdb.is_file())

        props.vdb_path = str(generated_vdb)
        self.assert_operator_finished(bpy.ops.blend_et.volume_render_import_vdb())
        self.assertEqual(
            2, len([obj for obj in bpy.data.objects if obj.type == "VOLUME"])
        )

    def test_npz_field_import(self):
        data = self.gaussian_volume((5, 6, 7))
        npz_path = self.workdir / "fields.npz"
        np.savez(npz_path, density=data, ignored=np.zeros_like(data))

        props = bpy.context.scene.blend_et_volume_render
        props.numpy_path = str(npz_path)
        props.npz_key = "density"
        self._configure_crop(data.shape)

        self.assert_operator_finished(bpy.ops.blend_et.volume_render_import_numpy())
        self.assertTrue(any(obj.type == "VOLUME" for obj in bpy.data.objects))
