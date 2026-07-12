from __future__ import annotations

from pathlib import Path
import subprocess
from unittest import mock

import bpy

from blend_et.latex import utils as latex_utils
from .common import BlenderIntegrationTest


SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="32" height="16" viewBox="0 0 32 16">
<path d="M 1,14 L 8,2 L 15,14 Z M 18,14 L 24,2 L 30,14" fill="black"/>
</svg>
"""


def fake_tex_run(args, **kwargs):
    if Path(args[0]).name.lower().startswith("dvisvgm"):
        Path("temp.svg").write_text(SVG, encoding="utf-8")
    return subprocess.CompletedProcess(
        args=args, returncode=0, stdout="fake compiler ok"
    )


class LatexTests(BlenderIntegrationTest):
    def _configure(self):
        props = bpy.context.scene.blend_et_latex
        props.latex_code = r"$E=mc^2$"
        props.command_selection = "latex"
        props.custom_preamble_bool = False
        props.custom_material_bool = False
        props.text_scale = 0.01
        props.text_thickness = 0.01

    def test_latex_mesh(self):
        self._configure()
        with mock.patch.object(latex_utils.subprocess, "run", side_effect=fake_tex_run):
            self.assert_operator_finished(bpy.ops.blend_et.latex_compile_as_mesh())
        obj = bpy.data.objects.get("LaTeX Figure")
        self.assertIsNotNone(obj)
        self.assertEqual("MESH", obj.type)
        self.assertEqual(r"$E=mc^2$", obj["Original LaTeX Code"])

    def test_latex_grease_pencil(self):
        self._configure()
        with mock.patch.object(latex_utils.subprocess, "run", side_effect=fake_tex_run):
            self.assert_operator_finished(
                bpy.ops.blend_et.latex_compile_as_grease_pencil()
            )
        obj = bpy.data.objects.get("LaTeX Figure")
        self.assertIsNotNone(obj)
        self.assertEqual("GREASEPENCIL", obj.type)
