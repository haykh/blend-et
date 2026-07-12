from __future__ import annotations

import os
from pathlib import Path
import tempfile
from typing import cast
import unittest

import bpy
import numpy as np


class BlenderIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        artifacts = Path(os.environ["BLEND_ET_TEST_ARTIFACTS"])
        artifacts.mkdir(parents=True, exist_ok=True)
        if os.environ.get("BLEND_ET_TEST_KEEP_ARTIFACTS") == "1":
            cls._tempdir = None
            cls.workdir = artifacts / cls.__name__
            cls.workdir.mkdir(exist_ok=True)
        else:
            cls._tempdir = tempfile.TemporaryDirectory(
                prefix=f"{cls.__name__}_", dir=artifacts
            )
            cls.workdir = Path(cls._tempdir.name)

    @classmethod
    def tearDownClass(cls):
        if cls._tempdir is not None:
            cls._tempdir.cleanup()

    def setUp(self):
        self.clear_scene()

    @staticmethod
    def clear_scene():
        if bpy.context.object is not None and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        for obj in list(bpy.data.objects):
            bpy.data.objects.remove(obj, do_unlink=True)

        scene = bpy.context.scene
        for collection in list(bpy.data.collections):
            bpy.data.collections.remove(collection)
        for material in list(bpy.data.materials):
            bpy.data.materials.remove(material)
        for node_group in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(node_group)
        for mesh in list(bpy.data.meshes):
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        for curve in list(bpy.data.curves):
            if curve.users == 0:
                bpy.data.curves.remove(curve)

        for prop_name in (
            "blend_et_volume_render",
            "blend_et_fieldlines",
            "blend_et_pointcloud",
            "blend_et_annotations",
        ):
            props = getattr(scene, prop_name, None)
            if props is not None and hasattr(props, "uuid"):
                props.uuid = 0

    def assert_operator_finished(self, result):
        self.assertEqual({"FINISHED"}, set(result))

    @staticmethod
    def gaussian_volume(shape=(8, 7, 6)) -> np.ndarray:
        z, y, x = np.indices(shape, dtype=np.float32)
        center = (np.asarray(shape, dtype=np.float32) - 1.0) / 2.0
        radius2 = (z - center[0]) ** 2 + (y - center[1]) ** 2 + (x - center[2]) ** 2
        return np.exp(-radius2 / 5.0).astype(np.float32)

    @staticmethod
    def geometry_node_group(obj: bpy.types.Object) -> bpy.types.NodeTree:
        modifiers = [modifier for modifier in obj.modifiers if modifier.type == "NODES"]
        if not modifiers or modifiers[0].node_group is None:
            raise AssertionError(f"{obj.name} has no Geometry Nodes group")
        return cast(bpy.types.NodeTree, modifiers[0].node_group)
