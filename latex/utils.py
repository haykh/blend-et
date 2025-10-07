import bpy  # type: ignore
import os, glob, math, subprocess


def _error_msg(message, title):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon="ERROR")


def Rel_to_abs(sp_name):
    if bpy.context.scene.blend_et_latex[sp_name].startswith("//"):
        abs_path = os.path.abspath(
            bpy.path.abspath(bpy.context.scene.blend_et_latex[sp_name])
        )
        bpy.context.scene.blend_et_latex[sp_name] = abs_path


def Compile_with_latex(
    self,
    context,
    latex_code,
    custom_latex_path,
    custom_pdflatex_path,
    custom_xelatex_path,
    custom_lualatex_path,
    custom_dvisvgm_path,
    command_selection,
    text_scale,
    text_thickness,
    x_loc,
    y_loc,
    z_loc,
    x_rot,
    y_rot,
    z_rot,
    custom_preamble_bool,
    temp_dir,
    custom_material_bool,
    custom_material_value,
    compile_mode,
    preamble_path=None,
):

    # Set current directory to temp_directory
    current_dir = os.getcwd()
    os.chdir(temp_dir)
    temp_dir = os.path.realpath(temp_dir)

    # Create temp latex file with specified preamble.
    temp_file_name = temp_dir + os.sep + "temp"
    if custom_preamble_bool:
        shutil.copy(preamble_path, temp_file_name + ".tex")  # type: ignore
        temp = open(temp_file_name + ".tex", "a")
    else:
        temp = open(temp_file_name + ".tex", "a")
        default_preamble = (
            "\\documentclass{amsart}\n\\usepackage{amssymb,amsfonts}\n\\usepackage{tikz}"
            "\n\\usepackage{tikz-cd}\n\\pagestyle{empty}\n\\thispagestyle{empty}"
        )
        temp.write(default_preamble)

    # Add latex code to temp.tex and close the file.
    temp.write("\n\\begin{document}\n" + latex_code + "\n\\end{document}")
    temp.close()

    # Try to compile temp.tex and create an svg file
    try:
        # Updates 'PATH' to include reference to folder containing latex and dvisvgm executable files.
        latex_exec_path = "/Library/TeX/texbin"
        local_env = os.environ.copy()
        local_env["PATH"] = latex_exec_path + os.pathsep + local_env["PATH"]

        if custom_latex_path != "" and custom_latex_path != "/Library/TeX/texbin":
            local_env["PATH"] = custom_latex_path + os.pathsep + local_env["PATH"]
        if (
            custom_pdflatex_path != ""
            and custom_pdflatex_path != "/Library/TeX/texbin"
            and custom_pdflatex_path != custom_latex_path
        ):
            local_env["PATH"] = custom_pdflatex_path + os.pathsep + local_env["PATH"]
        if (
            custom_xelatex_path != ""
            and custom_xelatex_path != "/Library/TeX/texbin"
            and custom_xelatex_path != custom_latex_path
            and custom_xelatex_path != custom_pdflatex_path
        ):
            local_env["PATH"] = custom_xelatex_path + os.pathsep + local_env["PATH"]
        if (
            custom_lualatex_path != ""
            and custom_lualatex_path != "/Library/TeX/texbin"
            and custom_lualatex_path != custom_latex_path
            and custom_lualatex_path != custom_pdflatex_path
            and custom_lualatex_path != custom_xelatex_path
        ):
            local_env["PATH"] = custom_lualatex_path + os.pathsep + local_env["PATH"]
        if (
            custom_dvisvgm_path != ""
            and custom_dvisvgm_path != "/Library/TeX/texbin"
            and custom_dvisvgm_path != custom_latex_path
            and custom_dvisvgm_path != custom_pdflatex_path
            and custom_dvisvgm_path != custom_xelatex_path
            and custom_dvisvgm_path != custom_lualatex_path
        ):
            local_env["PATH"] = custom_dvisvgm_path + os.pathsep + local_env["PATH"]
        if command_selection == "latex":
            tex_process = subprocess.run(
                ["latex", "-interaction=nonstopmode", temp_file_name + ".tex"],
                env=local_env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        elif command_selection == "pdflatex":
            tex_process = subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-output-format=dvi",
                    temp_file_name + ".tex",
                ],
                env=local_env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        elif command_selection == "xelatex":
            tex_process = subprocess.run(
                [
                    "xelatex",
                    "-interaction=nonstopmode",
                    "-no-pdf",
                    temp_file_name + ".tex",
                ],
                env=local_env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        else:
            tex_process = subprocess.run(
                [
                    "lualatex",
                    "-interaction=nonstopmode",
                    "-output-format=dvi",
                    temp_file_name + ".tex",
                ],
                env=local_env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        dvisvgm_process = subprocess.run(
            ["dvisvgm", "--no-fonts", temp_file_name + ".dvi"],
            env=local_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        svg_file_list = glob.glob("*.svg")
        bpy.ops.object.select_all(action="DESELECT")

        if len(svg_file_list) == 0:
            self.report(
                {"ERROR"},
                "Please check your LaTeX code for errors and that LaTeX and dvisvgm are properly "
                "installed and their paths are specified correctly. Also, if using a custom preamble, check that it is formatted correctly. \n"
                "Tex return code " + str(tex_process.returncode) + "\n"
                "dvi2svgm return code " + str(dvisvgm_process.returncode) + "\n"
                "Tex error message: " + str(tex_process.stdout) + "\n"
                "dvi2svgm error message: " + str(dvisvgm_process.stdout),
            )

        else:
            svg_file_path = temp_dir + os.sep + svg_file_list[0]

            objects_before_import = bpy.data.objects[:]
            # Import svg into blender as curve
            bpy.ops.import_curve.svg(filepath=svg_file_path)

            # Select imported objects
            imported_curve = [
                x for x in bpy.data.objects if x not in objects_before_import
            ]
            active_obj = imported_curve[0]
            context.view_layer.objects.active = active_obj
            for x in imported_curve:
                x.select_set(True)

            # Convert to mesh
            bpy.ops.object.convert(target="MESH")

            # Join components to merge into single object
            bpy.ops.object.join()

            # Adjust scale, location, and rotation.
            bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS", center="MEDIAN")
            active_obj.scale = (600 * text_scale, 600 * text_scale, 600 * text_scale)
            bpy.ops.object.transform_apply(location=False, scale=True, rotation=False)
            active_obj.location = (x_loc, y_loc, z_loc)
            active_obj.rotation_euler = (
                math.radians(x_rot),
                math.radians(y_rot),
                math.radians(z_rot),
            )

            # Move mesh to scene collection and delete the temp.svg collection. Then rename mesh.
            temp_svg_collection = active_obj.users_collection[0]
            bpy.ops.object.move_to_collection(collection_index=0)
            bpy.data.collections.remove(temp_svg_collection)
            active_obj.name = "LaTeX Figure"

            if custom_material_bool:
                active_obj.material_slots[0].material = custom_material_value

            if compile_mode == "grease pencil":
                # Convert to grease pencil
                bpy.ops.object.convert(
                    target="GREASEPENCIL",
                    thickness=1,
                    offset=0,
                )

                # Moves to scene collection, fixes name.
                bpy.ops.object.move_to_collection(collection_index=0)
                bpy.context.selected_objects[0].name = "LaTeX Figure"
                if custom_material_bool:
                    bpy.context.selected_objects[0].material_slots[
                        0
                    ].material = custom_material_value
            elif compile_mode == "mesh":
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.mesh.select_all(action="SELECT")
                bpy.ops.mesh.extrude_region_move(
                    TRANSFORM_OT_translate={
                        "value": (0, 0, text_scale * text_thickness),
                        "orient_type": "NORMAL",
                    },
                )
                bpy.ops.object.mode_set(mode="OBJECT")

            else:
                _error_msg("Unknown compile mode.", "Error")
            bpy.context.selected_objects[0]["Original LaTeX Code"] = latex_code

    except FileNotFoundError as e:
        _error_msg(
            "Please check that LaTeX is installed on your system and that its path is specified correctly.",
            "Compilation Error",
        )
    except subprocess.CalledProcessError as e:
        _error_msg(
            "Please check your LaTeX code for errors and that LaTeX and dvisvgm are properly "
            "installed and their paths are specified correctly. Also, if using a custom preamble, check that it is formatted correctly. "
            "Return code: " + str(e.returncode) + " " + str(e.output),
            "Compilation Error",
        )
    finally:
        os.chdir(current_dir)
        print("Finished trying to compile LaTeX and create an svg file.")
