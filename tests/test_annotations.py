from __future__ import annotations

import bpy

from .common import BlenderIntegrationTest


class AnnotationTests(BlenderIntegrationTest):
    def test_axes_grid(self):
        self.assert_operator_finished(bpy.ops.blend_et.annotations_add_axes_grid())
        obj = bpy.data.objects.get("AxesGrid_0000")
        self.assertIsNotNone(obj)
        self.assertIn("GeometryNodes", obj.modifiers)
        self.assertIsNotNone(obj.active_material)

    def test_arrow(self):
        self.assert_operator_finished(bpy.ops.blend_et.annotations_add_arrow())
        obj = bpy.data.objects.get("Arrow_0000")
        self.assertIsNotNone(obj)
        self.assertIn("GeometryNodes", obj.modifiers)
        self.assertIn("EdgeSplit", obj.modifiers)

    def test_origin_axes(self):
        self.assert_operator_finished(bpy.ops.blend_et.annotations_add_axes())
        obj = bpy.data.objects.get("Axes_0000")
        self.assertIsNotNone(obj)
        self.assertIn("GeometryNodes", obj.modifiers)
        self.assertIn("ShadingColor", obj.active_material.node_tree.nodes)
