import bpy  # type: ignore

import tempfile

from .utils import Compile_with_latex


class Latex_CompileAsMesh(bpy.types.Operator):
    bl_idname = "blend_et.latex_compile_as_mesh"
    bl_label = "Compile LaTeX as mesh"

    def execute(self, context):
        props = context.scene.blend_et_latex
        if (
            props.latex_code == ""
            and props.custom_preamble_bool
            and props.preamble_path == ""
        ):
            self.report(
                {"ERROR"},
                "No LaTeX code has been entered and no preamble file has been chosen. "
                "Please enter some LaTeX code and choose a .tex file for the preamble",
            )
        elif props.custom_material_bool and props.custom_material_value is None:
            self.report(
                {"ERROR"}, "No material has been chosen. Please choose a material."
            )
        elif props.latex_code == "":
            self.report(
                {"ERROR"},
                "No LaTeX code has been entered. Please enter some LaTeX code.",
            )
        elif props.custom_preamble_bool and props.preamble_path == "":
            self.report(
                {"ERROR"}, "No preamble file has been chosen. Please choose a file."
            )
        else:
            with tempfile.TemporaryDirectory() as temp_dir:
                Compile_with_latex(
                    self,
                    context,
                    props.latex_code,
                    props.custom_latex_path,
                    props.custom_pdflatex_path,
                    props.custom_xelatex_path,
                    props.custom_lualatex_path,
                    props.custom_dvisvgm_path,
                    props.command_selection,
                    props.text_scale,
                    props.text_thickness,
                    props.x_loc,
                    props.y_loc,
                    props.z_loc,
                    props.x_rot,
                    props.y_rot,
                    props.z_rot,
                    props.custom_preamble_bool,
                    temp_dir,
                    props.custom_material_bool,
                    props.custom_material_value,
                    "mesh",
                    props.preamble_path,
                )
        return {"FINISHED"}


class Latex_CompileAsGreasePencil(bpy.types.Operator):
    bl_idname = "blend_et.latex_compile_as_grease_pencil"
    bl_label = "Compile LaTeX as grease pencil"

    def execute(self, context):
        props = context.scene.blend_et_latex
        if (
            props.latex_code == ""
            and props.custom_preamble_bool
            and props.preamble_path == ""
        ):
            self.report(
                {"ERROR"},
                "No LaTeX code has been entered and no preamble file has been chosen. Please enter some "
                "LaTeX code and choose a .tex file for the preamble",
            )
        elif props.custom_material_bool and props.custom_material_value is None:
            self.report(
                {"ERROR"}, "No material has been chosen. Please choose a material."
            )
        elif props.latex_code == "":
            self.report(
                {"ERROR"},
                "No LaTeX code has been entered. Please enter some LaTeX code.",
            )
        elif props.custom_preamble_bool and props.preamble_path == "":
            self.report(
                {"ERROR"}, "No preamble file has been chosen. Please choose a file."
            )
        else:
            with tempfile.TemporaryDirectory() as temp_dir:
                Compile_with_latex(
                    self,
                    context,
                    props.latex_code,
                    props.custom_latex_path,
                    props.custom_pdflatex_path,
                    props.custom_xelatex_path,
                    props.custom_lualatex_path,
                    props.custom_dvisvgm_path,
                    props.command_selection,
                    props.text_scale,
                    props.text_thickness,
                    props.x_loc,
                    props.y_loc,
                    props.z_loc,
                    props.x_rot,
                    props.y_rot,
                    props.z_rot,
                    props.custom_preamble_bool,
                    temp_dir,
                    props.custom_material_bool,
                    props.custom_material_value,
                    "grease pencil",
                    props.preamble_path,
                )
        return {"FINISHED"}
