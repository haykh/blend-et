bl_info = {
    "name": "SciBlend",
    "author": "hayk",
    "version": (0, 1, 0),
    "blender": (4, 5, 0),
    "location": "N panel > SciBlend",
    "description": "Collection of tools for scientific visualization and rendering.",
    "category": "Object",
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# The LaTeX support is adapted from the very nice ghseeli/latex2blender plugin
# github link: https://github.com/ghseeli/latex2blender
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import bpy  # type: ignore
import bpy.utils.previews  # type: ignore
import numpy as np  # type: ignore
import os
import shutil
import tempfile
import subprocess
import glob
import math


# -----------------------------
# Helpers
# -----------------------------
def ErrorMessageBox(message, title):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon="ERROR")


def _compile_with_latex(
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
                bpy.context.selected_objects[0].data.use_auto_smooth = True

            else:
                ErrorMessageBox("Unknown compile mode.", "Error")
            bpy.context.selected_objects[0]["Original LaTeX Code"] = latex_code

    except FileNotFoundError as e:
        ErrorMessageBox(
            "Please check that LaTeX is installed on your system and that its path is specified correctly.",
            "Compilation Error",
        )
    except subprocess.CalledProcessError as e:
        ErrorMessageBox(
            "Please check your LaTeX code for errors and that LaTeX and dvisvgm are properly "
            "installed and their paths are specified correctly. Also, if using a custom preamble, check that it is formatted correctly. "
            "Return code: " + str(e.returncode) + " " + str(e.output),
            "Compilation Error",
        )
    finally:
        os.chdir(current_dir)
        print("Finished trying to compile LaTeX and create an svg file.")


COLORMAPS = {
    "fire": [
        (0.0, (0.0, 0.0, 0.0)),
        (0.0625, (0.19607843, 0.0, 0.0)),
        (0.125, (0.29019608, 0.0, 0.0)),
        (0.1875, (0.38823529, 0.00392157, 0.0)),
        (0.25, (0.49019608, 0.00784314, 0.0)),
        (0.3125, (0.59607843, 0.01176471, 0.0)),
        (0.375, (0.70588235, 0.01960784, 0.0)),
        (0.4375, (0.81960784, 0.03529412, 0.0)),
        (0.5, (0.92941176, 0.07843137, 0.0)),
        (0.5625, (0.98431373, 0.25098039, 0.0)),
        (0.625, (0.99607843, 0.40784314, 0.0)),
        (0.6875, (1.0, 0.5372549, 0.0)),
        (0.75, (1.0, 0.65098039, 0.00392157)),
        (0.8125, (1.0, 0.75686275, 0.01176471)),
        (0.875, (1.0, 0.85490196, 0.03529412)),
        (0.9375, (1.0, 0.95294118, 0.14117647)),
        (1.0, (1.0, 1.0, 1.0)),
    ],
    "viridis": [
        (0.0, (0.267004, 0.004874, 0.329415)),
        (0.0625, (0.282327, 0.094955, 0.417331)),
        (0.125, (0.278826, 0.17549, 0.483397)),
        (0.1875, (0.258965, 0.251537, 0.524736)),
        (0.25, (0.229739, 0.322361, 0.545706)),
        (0.3125, (0.19943, 0.387607, 0.554642)),
        (0.375, (0.172719, 0.448791, 0.557885)),
        (0.4375, (0.149039, 0.508051, 0.55725)),
        (0.5, (0.127568, 0.566949, 0.550556)),
        (0.5625, (0.120638, 0.625828, 0.533488)),
        (0.625, (0.157851, 0.683765, 0.501686)),
        (0.6875, (0.24607, 0.73891, 0.452024)),
        (0.75, (0.369214, 0.788888, 0.382914)),
        (0.8125, (0.515992, 0.831158, 0.294279)),
        (0.875, (0.678489, 0.863742, 0.189503)),
        (0.9375, (0.845561, 0.887322, 0.099702)),
        (1.0, (0.993248, 0.906157, 0.143936)),
    ],
    "plasma": [
        (0.0, (0.050383, 0.029803, 0.527975)),
        (0.0625, (0.193374, 0.018354, 0.59033)),
        (0.125, (0.299855, 0.009561, 0.631624)),
        (0.1875, (0.399411, 0.000859, 0.656133)),
        (0.25, (0.494877, 0.01199, 0.657865)),
        (0.3125, (0.584391, 0.068579, 0.632812)),
        (0.375, (0.665129, 0.138566, 0.585582)),
        (0.4375, (0.736019, 0.209439, 0.527908)),
        (0.5, (0.798216, 0.280197, 0.469538)),
        (0.5625, (0.853319, 0.351553, 0.413734)),
        (0.625, (0.901807, 0.425087, 0.359688)),
        (0.6875, (0.942598, 0.502639, 0.305816)),
        (0.75, (0.973416, 0.585761, 0.25154)),
        (0.8125, (0.991365, 0.675355, 0.198453)),
        (0.875, (0.993033, 0.77172, 0.154808)),
        (0.9375, (0.974443, 0.874622, 0.144061)),
        (1.0, (0.940015, 0.975158, 0.131326)),
    ],
    "inferno": [
        (0.0, (0.001462, 0.000466, 0.013866)),
        (0.0625, (0.042253, 0.028139, 0.141141)),
        (0.125, (0.129285, 0.047293, 0.290788)),
        (0.1875, (0.238273, 0.036621, 0.396353)),
        (0.25, (0.3415, 0.062325, 0.429425)),
        (0.3125, (0.441207, 0.099338, 0.431594)),
        (0.375, (0.54092, 0.134729, 0.415123)),
        (0.4375, (0.640135, 0.171438, 0.381065)),
        (0.5, (0.735683, 0.215906, 0.330245)),
        (0.5625, (0.822386, 0.275197, 0.266085)),
        (0.625, (0.894305, 0.353399, 0.193584)),
        (0.6875, (0.946965, 0.449191, 0.115272)),
        (0.75, (0.978422, 0.557937, 0.034931)),
        (0.8125, (0.987874, 0.675267, 0.065257)),
        (0.875, (0.974638, 0.797692, 0.206332)),
        (0.9375, (0.947594, 0.917399, 0.410665)),
        (1.0, (0.988362, 0.998364, 0.644924)),
    ],
    "magma": [
        (0.0, (0.001462, 0.000466, 0.013866)),
        (0.0625, (0.039608, 0.03109, 0.133515)),
        (0.125, (0.113094, 0.065492, 0.276784)),
        (0.1875, (0.211718, 0.061992, 0.418647)),
        (0.25, (0.316654, 0.07169, 0.48538)),
        (0.3125, (0.414709, 0.110431, 0.504662)),
        (0.375, (0.512831, 0.148179, 0.507648)),
        (0.4375, (0.613617, 0.181811, 0.498536)),
        (0.5, (0.716387, 0.214982, 0.47529)),
        (0.5625, (0.816914, 0.255895, 0.436461)),
        (0.625, (0.904281, 0.31961, 0.388137)),
        (0.6875, (0.960949, 0.418323, 0.35963)),
        (0.75, (0.9867, 0.535582, 0.38221)),
        (0.8125, (0.996096, 0.653659, 0.446213)),
        (0.875, (0.996898, 0.769591, 0.534892)),
        (0.9375, (0.99244, 0.88433, 0.640099)),
        (1.0, (0.987053, 0.991438, 0.749504)),
    ],
    "jet": [
        (0.0, (0.0, 0.0, 0.5)),
        (0.0625, (0.0, 0.0, 0.785204991087344)),
        (0.125, (0.0, 0.00196078431372549, 1.0)),
        (0.1875, (0.0, 0.2529411764705882, 1.0)),
        (0.25, (0.0, 0.503921568627451, 1.0)),
        (0.3125, (0.0, 0.7549019607843137, 1.0)),
        (0.375, (0.08538899430740036, 1.0, 0.8823529411764706)),
        (0.4375, (0.2877925363693864, 1.0, 0.6799493991144845)),
        (0.5, (0.4901960784313725, 1.0, 0.4775458570524984)),
        (0.5625, (0.6925996204933585, 1.0, 0.27514231499051234)),
        (0.625, (0.8950031625553446, 1.0, 0.07273877292852626)),
        (0.6875, (1.0, 0.8140885984023241, 0.0)),
        (0.75, (1.0, 0.5816993464052289, 0.0)),
        (0.8125, (1.0, 0.34931009440813376, 0.0)),
        (0.875, (1.0, 0.11692084241103862, 0.0)),
        (0.9375, (0.7673796791443852, 0.0, 0.0)),
        (1.0, (0.5, 0.0, 0.0)),
    ],
    "turbo": [
        (0.0, (0.18995, 0.07176, 0.23217)),
        (0.0625, (0.25107, 0.25237, 0.63374)),
        (0.125, (0.27628, 0.42118, 0.89123)),
        (0.1875, (0.25862, 0.57958, 0.99876)),
        (0.25, (0.15844, 0.73551, 0.92305)),
        (0.3125, (0.09267, 0.86554, 0.7623)),
        (0.375, (0.19659, 0.94901, 0.59466)),
        (0.4375, (0.42778, 0.99419, 0.38575)),
        (0.5, (0.64362, 0.98999, 0.23356)),
        (0.5625, (0.80473, 0.92452, 0.20459)),
        (0.625, (0.93301, 0.81236, 0.22667)),
        (0.6875, (0.99314, 0.67408, 0.20348)),
        (0.75, (0.9836, 0.49291, 0.12849)),
        (0.8125, (0.92105, 0.31489, 0.05475)),
        (0.875, (0.81608, 0.18462, 0.01809)),
        (0.9375, (0.66449, 0.08436, 0.00424)),
        (1.0, (0.4796, 0.01583, 0.01055)),
    ],
    "twilight": [
        (0.0, (0.8857501584075443, 0.8500092494306783, 0.8879736506427196)),
        (0.0625, (0.7675110850441786, 0.8098007598713145, 0.8325281663805967)),
        (0.125, (0.5830148703693241, 0.7095888767699747, 0.7792578182047659)),
        (0.1875, (0.4480247093358917, 0.5923833145214658, 0.7557417647410792)),
        (0.25, (0.38407269378943537, 0.46139018782416635, 0.7309466543290268)),
        (0.3125, (0.3698798032902536, 0.31638410101153364, 0.6770375543809057)),
        (0.375, (0.3506030444193101, 0.1659512998472086, 0.5614796470399323)),
        (0.4375, (0.2700863774911405, 0.07548367558427554, 0.36056376228111864)),
        (0.5, (0.18488035509396164, 0.07942573027972388, 0.21307651648984993)),
        (0.5625, (0.29128515387578635, 0.0748990498474667, 0.25755101595750435)),
        (0.625, (0.4538300508699989, 0.11622183788331528, 0.3097044124984492)),
        (0.6875, (0.5965991810912237, 0.207212956082026, 0.3125852303112123)),
        (0.75, (0.6980608153581771, 0.3382897632604862, 0.3220747885521809)),
        (0.8125, (0.7625733355405261, 0.48718906673415824, 0.38675335037837993)),
        (0.875, (0.8002941538975398, 0.6409821330674986, 0.5373053518514104)),
        (0.9375, (0.8489224556311764, 0.7799202140765015, 0.7466371929366437)),
        (1.0, (0.8857115512284565, 0.8500218611585632, 0.8857253899008712)),
    ],
    "RdBu": [
        (0.0, (0.403921568627451, 0.0, 0.12156862745098039)),
        (0.0625, (0.5884659746251442, 0.05905420991926182, 0.1510957324106113)),
        (0.125, (0.7340253748558246, 0.16608996539792387, 0.20261437908496732)),
        (0.1875, (0.8226066897347174, 0.34325259515570933, 0.28627450980392155)),
        (0.25, (0.8991926182237601, 0.5144175317185697, 0.4079200307574009)),
        (0.3125, (0.9617070357554787, 0.6761245674740484, 0.546943483275663)),
        (0.375, (0.9838523644752019, 0.8089965397923875, 0.7167243367935409)),
        (0.4375, (0.9829296424452134, 0.9018838908112264, 0.8542099192618224)),
        (0.5, (0.9657054978854287, 0.9672433679354094, 0.9680891964628989)),
        (0.5625, (0.8722029988465976, 0.9229527104959632, 0.9508650519031142)),
        (0.625, (0.7517877739331029, 0.8635909265667053, 0.9217993079584775)),
        (0.6875, (0.5967704728950406, 0.7848519800076895, 0.8775086505190313)),
        (0.75, (0.4085351787773935, 0.6687427912341408, 0.8145328719723184)),
        (0.8125, (0.24183006535947713, 0.5487889273356401, 0.750557477893118)),
        (0.875, (0.15816993464052287, 0.43806228373702427, 0.6939638600538255)),
        (0.9375, (0.08419838523644753, 0.31280276816609, 0.5534025374855824)),
        (1.0, (0.0196078431372549, 0.18823529411764706, 0.3803921568627451)),
    ],
    "BrBG": [
        (0.0, (0.32941176470588235, 0.18823529411764706, 0.0196078431372549)),
        (0.0625, (0.46720492118415996, 0.26943483275663205, 0.031910803537101115)),
        (0.125, (0.6000000000000001, 0.3656286043829296, 0.07420222991157246)),
        (0.1875, (0.7254901960784313, 0.48373702422145326, 0.16032295271049596)),
        (0.25, (0.8129950019223375, 0.635832372164552, 0.33640907343329485)),
        (0.3125, (0.8868896578239138, 0.7812379853902344, 0.5278738946559014)),
        (0.375, (0.9434832756632064, 0.8747404844290657, 0.7001153402537484)),
        (0.4375, (0.9631680123029605, 0.9297962322183776, 0.84159938485198)),
        (0.5, (0.9572472126105345, 0.9599384851980008, 0.9595540176855056)),
        (0.5625, (0.8440599769319495, 0.9328719723183391, 0.9201845444059977)),
        (0.625, (0.7039600153787008, 0.8864282968089198, 0.8592848904267592)),
        (0.6875, (0.5292579777008846, 0.8150711264898117, 0.7707035755478664)),
        (0.75, (0.346251441753172, 0.6918108419838525, 0.653056516724337)),
        (0.8125, (0.1758554402153018, 0.5620146097654748, 0.530642060745867)),
        (0.875, (0.0479046520569012, 0.44144559784698195, 0.4100730488273741)),
        (0.9375, (0.002306805074971165, 0.33217993079584773, 0.2943483275663207)),
        (1.0, (0.0, 0.23529411764705882, 0.18823529411764706)),
    ],
}


def _resolve_cmap_id(val):
    # Convert whatever the property gives us into a valid identifier string.
    if isinstance(val, str):
        return val
    ids = list(COLORMAPS.keys())
    try:
        idx = int(val)
    except (TypeError, ValueError):
        idx = 0
    if 0 <= idx < len(ids):
        return ids[idx]
    # Fallback
    return next(iter(COLORMAPS.keys()), "Default")


_PREVIEW_COLLECTIONS = {}


def _build_colormap_previews():
    if "colormaps" in _PREVIEW_COLLECTIONS:
        return _PREVIEW_COLLECTIONS["colormaps"]

    def _lerp(a, b, t):
        return a + (b - a) * t

    def _sample_stops(stops, t):
        """Return (r,g,b,a) at t in [0..1] by linear interpolation of stops."""

        s = sorted(stops, key=lambda x: x[0])
        if t <= s[0][0]:
            c = s[0][1]
            return (c[0], c[1], c[2], c[3] if len(c) > 3 else 1.0)
        for i in range(len(s) - 1):
            t0, c0 = s[i]
            t1, c1 = s[i + 1]
            if t <= t1 or i == len(s) - 2:
                u = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
                a0 = c0[3] if len(c0) > 3 else 1.0
                a1 = c1[3] if len(c1) > 3 else 1.0
                return (
                    _lerp(c0[0], c1[0], u),
                    _lerp(c0[1], c1[1], u),
                    _lerp(c0[2], c1[2], u),
                    _lerp(a0, a1, u),
                )
        c = s[-1][1]
        return (c[0], c[1], c[2], c[3] if len(c) > 3 else 1.0)

    def _render_gradient_pixels(stops, w, h, vertical=False):

        px = [0.0] * (w * h * 4)
        for y in range(h):
            for x in range(w):
                t = (y / (h - 1)) if vertical else (x / (w - 1))
                r, g, b, a = _sample_stops(stops, t)
                i = (y * w + x) * 4
                px[i : i + 4] = (r, g, b, a)
        return px

    pcoll = bpy.utils.previews.new()
    img_w, img_h = 128, 32
    ico_w, ico_h = 64, 64
    for cm_id, stops in COLORMAPS.items():
        p = pcoll.new(cm_id)
        p.image_size = (img_w, img_h)
        p.image_pixels_float[:] = _render_gradient_pixels(stops, img_w, img_h)
        p.icon_size = (ico_w, ico_h)
        p.icon_pixels_float[:] = _render_gradient_pixels(stops, ico_w, ico_h)
    _PREVIEW_COLLECTIONS["colormaps"] = pcoll
    return pcoll


def _free_colormap_previews():
    for pcoll in _PREVIEW_COLLECTIONS.values():
        bpy.utils.previews.remove(pcoll)
    _PREVIEW_COLLECTIONS.clear()


def _static_enum_items():
    # Always valid, even if previews aren't built yet.
    # Uses a built-in icon ('COLOR') as a fallback.
    ids = list(COLORMAPS.keys())
    if not ids:
        return [("Default", "Default", "Colormap", "COLOR", 0)]
    return [(cm_id, cm_id, "Colormap", "COLOR", i) for i, cm_id in enumerate(ids)]


def enum_colormap_items(self, context):
    """
    Dynamic items for the EnumProperty. If preview icons are not ready yet
    (e.g., during initial registration), fall back to static items so the
    property can register successfully.
    """
    try:
        pcoll = _PREVIEW_COLLECTIONS.get("colormaps", None)
        if pcoll is None:
            # Previews not built yet (or freed) -> safe fallback (no gradients)
            return _static_enum_items()

        items = []
        ids = list(COLORMAPS.keys())
        for i, cm_id in enumerate(ids):
            # If the preview is missing for any reason, fall back to a built-in icon.
            ip = pcoll.get(cm_id)
            icon = (ip.icon_id if ip else 0) or "COLOR"
            items.append((cm_id, cm_id, "Colormap", icon, i))

        # If COLORMAPS is empty or something went wrong, never return [].
        return items or _static_enum_items()

    except Exception as e:
        print(f"enum_colormap_items fallback due to error: {e}")
        return _static_enum_items()


def _apply_stops_to_colorramp(ramp: bpy.types.ColorRamp, stops):
    s = sorted(stops, key=lambda x: x[0])
    # Ensure correct count
    while len(ramp.elements) > len(s):
        ramp.elements.remove(ramp.elements[-1])
    while len(ramp.elements) < len(s):
        ramp.elements.new(0.5)
    # Write positions/colors
    for elem, (t, col) in zip(ramp.elements, s):
        elem.position = max(0.0, min(1.0, float(t)))
        if len(col) == 4:
            elem.color = col
        else:
            r, g, b = col
            elem.color = (r, g, b, 1.0)
    ramp.color_mode = "RGB"
    ramp.interpolation = "LINEAR"


def _stops_for_colormap(cm_id, reverse=False):
    """Return the stop list for a given colormap id, optionally reversed (_r style)."""
    # Fallback to the first map if id is missing
    first = next(iter(COLORMAPS.keys()))
    stops = COLORMAPS.get(cm_id, COLORMAPS[first])
    if not reverse:
        return stops
    # Reverse: color at 1 - t. Keep stops sorted ascending after transform.
    rev = [(1.0 - t, col) for (t, col) in reversed(stops)]
    rev.sort(key=lambda x: x[0])
    return rev


def _create_or_reset_volume_material(name) -> bpy.types.Material:
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
    else:
        if not mat.use_nodes:
            mat.use_nodes = True

    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links

    def _get_or_new(nodes, type_id, name=None, label=None):
        n = nodes.get(name) if name else None
        if n is None:
            n = nodes.new(type_id)
            if name:
                n.name = name
            if label:
                n.label = label
        return n

    vol_info = _get_or_new(nodes, "ShaderNodeVolumeInfo", "VolumeInfo", "Volume info")
    vol_info.location = (-50, -100)

    map_range = _get_or_new(nodes, "ShaderNodeMapRange", "ValueRemap", "Remap values")
    map_range.location = (150, 0)

    color_ramp = _get_or_new(nodes, "ShaderNodeValToRGB", "Colormap", "Colormap")
    color_ramp.location = (400, 300)

    float_curve = _get_or_new(
        nodes, "ShaderNodeFloatCurve", "OpacityCurve", "Opacity curve"
    )
    float_curve.location = (400, 0)

    multiply_1 = _get_or_new(
        nodes, "ShaderNodeMath", "MultiplyEmissivity", "Emissivity multiplier"
    )
    multiply_1.location = (400, -400)
    multiply_1.operation = "MULTIPLY"
    multiply_1.inputs[1].default_value = 2.0

    multiply_2 = _get_or_new(
        nodes, "ShaderNodeMath", "MultiplyOpacity", "Opacity multiplier"
    )
    multiply_2.location = (800, 0)
    multiply_2.operation = "MULTIPLY"
    multiply_2.inputs[1].default_value = 1.0

    vol = _get_or_new(nodes, "ShaderNodeVolumePrincipled", "Volume", "Volume shader")
    vol.location = (1100, 100)

    out = _get_or_new(
        nodes, "ShaderNodeOutputMaterial", "MaterialOutput", "Material Output"
    )
    out.location = (1400, 100)

    def _link_if_missing(a, b):
        if not b.links or all(l.from_socket is not a for l in b.links):
            links.new(a, b)

    _link_if_missing(vol_info.outputs["Density"], map_range.inputs["Value"])
    _link_if_missing(map_range.outputs["Result"], color_ramp.inputs["Fac"])
    _link_if_missing(map_range.outputs["Result"], float_curve.inputs["Value"])
    _link_if_missing(map_range.outputs["Result"], multiply_1.inputs[0])
    _link_if_missing(float_curve.outputs["Value"], multiply_2.inputs[0])
    _link_if_missing(color_ramp.outputs["Color"], vol.inputs["Color"])
    _link_if_missing(color_ramp.outputs["Color"], vol.inputs["Emission Color"])
    _link_if_missing(multiply_1.outputs["Value"], vol.inputs["Emission Strength"])
    _link_if_missing(multiply_2.outputs["Value"], vol.inputs["Density"])
    _link_if_missing(vol.outputs["Volume"], out.inputs["Volume"])

    cm_id = _resolve_cmap_id(getattr(mat, "volume_colormap", 0))
    rev = bool(getattr(mat, "volume_colormap_reversed", False))
    _apply_stops_to_colorramp(
        color_ramp.color_ramp, _stops_for_colormap(cm_id, reverse=rev)
    )

    return mat


def _store_histogram_on_material(
    mat: bpy.types.Material,
    hist: np.ndarray,
    vmin: float,
    vmax: float,
    q05: float,
    q95: float,
    width: int = 256,
    height: int = 256,
):
    bins = int(hist.size)
    # --- draw pixels ---
    px = np.empty((height, width, 4), dtype=np.float32)

    px[..., 0:3] = 0.22
    px[..., 3] = 1.0

    hmax = int(hist.max()) if hist.size else 1
    if hmax < 1:
        hmax = 1

    # normalized heights (0..H-10)
    heights = np.ceil((hist.astype(np.float32) / float(hmax)) * (height - 10)).astype(
        np.int32
    )

    # draw per-bin rectangles with >=2 px width
    for i in range(bins):
        x0 = int(i * width / bins)
        x1 = int((i + 1) * width / bins)
        if x1 <= x0:
            x1 = x0 + 1
        # ensure visible min width
        if x1 - x0 < 2:
            x1 = x0 + 2 if x0 + 2 <= width else width

        h = int(heights[i])
        if h > 0:
            px[0:h, x0:x1, 0:3] = 0.98
            px[0:h, x0:x1, 3] = 1.0

    if vmin < q05 < vmax:
        iq05 = int((q05 - vmin) / (vmax - vmin) * width)
        px[:, iq05 : min(iq05 + 2, width), 0] = 1.0
        px[:, iq05 : min(iq05 + 2, width), 1:3] = 0.2
        px[:, iq05 : min(iq05 + 2, width), 3] = 1.0

    if vmin < q95 < vmax:
        iq95 = int((q95 - vmin) / (vmax - vmin) * width)
        px[:, iq95 : min(iq95 + 2, width), 0] = 1.0
        px[:, iq95 : min(iq95 + 2, width), 1:3] = 0.2
        px[:, iq95 : min(iq95 + 2, width), 3] = 1.0

    img_name = f"SB_Hist_{mat.name}"
    img = bpy.data.images.get(img_name)
    if img is None:
        img = bpy.data.images.new(
            img_name, width=width, height=height, alpha=True, float_buffer=True
        )
        img.colorspace_settings.name = "Non-Color"
        img.alpha_mode = "STRAIGHT"
        img.use_fake_user = True
    else:
        if img.size[0] != width or img.size[1] != height:
            img.scale(width, height)

    img.pixels[:] = px.ravel().tolist()
    img.update()
    img.preview_ensure()

    # Store on the material
    mat.volume_hist_vmin = float(vmin)
    mat.volume_hist_vmax = float(vmax)
    mat.volume_hist_q05 = float(q05)
    mat.volume_hist_q95 = float(q95)
    mat.volume_hist_image = img
    mat.volume_hist_ready = True


def _clear_histogram_on_material(mat: bpy.types.Material):
    mat.volume_hist_vmin = 0.0
    mat.volume_hist_vmax = 0.0
    mat.volume_hist_q05 = 0.0
    mat.volume_hist_q95 = 0.0
    mat.volume_hist_image = None
    mat.volume_hist_ready = False


def _create_volume_object(context, store_path, abspath, uuid_str):
    scene = context.scene
    display_name = bpy.path.display_name_from_filepath(abspath)
    base_name = f"{display_name}_Volume_{uuid_str}"

    vol_data = bpy.data.volumes.new(name=base_name)
    vol_data.filepath = store_path

    vol_obj = bpy.data.objects.new(base_name, vol_data)
    collection = context.collection or context.scene.collection
    collection.objects.link(vol_obj)
    vol_obj.location = scene.cursor.location
    vol_obj.scale = (0.01, 0.01, 0.01)

    active_obj = vol_obj
    bpy.ops.object.select_all(action="DESELECT")
    active_obj.select_set(True)
    context.view_layer.objects.active = active_obj

    mat = _create_or_reset_volume_material(f"{display_name}_Material_{uuid_str}")
    if len(vol_obj.data.materials) == 0:
        vol_obj.data.materials.append(mat)
    else:
        vol_obj.data.materials[0] = mat

    return base_name, display_name, mat


def _rel_to_abs(sp_name):
    if bpy.context.scene.sci_blend_latex[sp_name].startswith("//"):
        abs_path = os.path.abspath(
            bpy.path.abspath(bpy.context.scene.sci_blend_latex[sp_name])
        )
        bpy.context.scene.sci_blend_latex[sp_name] = abs_path


# -----------------------------
# Callbacks
# -----------------------------
def _on_material_colormap_change(self, context):
    """Update callback: self is the Material that owns 'volume_colormap'."""
    if not getattr(self, "use_nodes", False) or not self.node_tree:
        return None
    nt = self.node_tree
    ramp_node = nt.nodes.get("Colormap")
    if ramp_node is None or ramp_node.type != "VALTORGB":
        # Make sure nodes exist and try again
        _create_or_reset_volume_material(self.name)
        ramp_node = nt.nodes.get("Colormap")
    if ramp_node:
        cm_id = _resolve_cmap_id(getattr(self, "volume_colormap", 0))
        rev = bool(getattr(self, "volume_colormap_reversed", False))
        stops = _stops_for_colormap(cm_id, reverse=rev)
        _apply_stops_to_colorramp(ramp_node.color_ramp, stops)
    return None


# -----------------------------
# Properties
# -----------------------------
class SciBlend_Tools_Props(bpy.types.PropertyGroup):
    background_color: bpy.props.FloatVectorProperty(
        name="Background color",
        description="Background color for the scene",
        subtype="COLOR",
        default=(0.0, 0.0, 0.0),
        min=0.0,
        max=1.0,
        size=3,
    )


class SciBlend_VolumeRender_Props(bpy.types.PropertyGroup):
    static_uuid: bpy.props.IntProperty(
        name="Static UUID",
        description="Static part of the UUID for the volume object",
        default=0,
    )

    vdb_path: bpy.props.StringProperty(
        name=".vdb",
        description="Path to .vdb file for volume rendering",
        subtype="FILE_PATH",
    )
    save_relative: bpy.props.BoolProperty(
        name="Store relative path",
        description="Store .vdb filepath relative to this .blend",
        default=False,
    )
    numpy_path: bpy.props.StringProperty(
        name=".npy / .npz",
        description="Path to a 3D NumPy array file",
        subtype="FILE_PATH",
    )
    npz_key: bpy.props.StringProperty(
        name="NPZ field",
        description="Dataset key inside .npz (leave empty for .npy)",
        default="",
    )
    numpy_axis_order: bpy.props.EnumProperty(
        name="Axis order",
        description="Order of axes in the input array",
        items=[
            ("ZYX", "ZYX (common)", "Array is (Z, Y, X)"),
            ("XYZ", "XYZ", "Array is (X, Y, Z)"),
            ("YZX", "YZX", "Array is (Y, Z, X)"),
            ("ZXY", "ZXY", "Array is (Z, X, Y)"),
            ("XZY", "XZY", "Array is (X, Z, Y)"),
            ("YXZ", "YXZ", "Array is (Y, X, Z)"),
        ],
        default="ZYX",
    )
    numpy_crop_xmin: bpy.props.IntProperty(
        name="X min",
        description="Crop array: minimum X index (inclusive)",
        default=0,
    )
    numpy_crop_xmax: bpy.props.IntProperty(
        name="X max",
        description="Crop array: maximum X index (exclusive)",
        default=-1,
    )
    numpy_crop_ymin: bpy.props.IntProperty(
        name="Y min",
        description="Crop array: minimum Y index (inclusive)",
        default=0,
    )
    numpy_crop_ymax: bpy.props.IntProperty(
        name="Y max",
        description="Crop array: maximum Y index (exclusive)",
        default=-1,
    )
    numpy_crop_zmin: bpy.props.IntProperty(
        name="Z min",
        description="Crop array: minimum Z index (inclusive)",
        default=0,
    )
    numpy_crop_zmax: bpy.props.IntProperty(
        name="Z max",
        description="Crop array: maximum Z index (exclusive)",
        default=-1,
    )


class SciBlend_Material_Props:
    @staticmethod
    def register():
        if hasattr(bpy.types.Material, "volume_colormap"):
            del bpy.types.Material.volume_colormap
        if hasattr(bpy.types.Material, "volume_colormap_reversed"):
            del bpy.types.Material.volume_colormap_reversed
        if hasattr(bpy.types.Material, "volume_hist_vmin"):
            del bpy.types.Material.volume_hist_vmin
        if hasattr(bpy.types.Material, "volume_hist_vmax"):
            del bpy.types.Material.volume_hist_vmax
        if hasattr(bpy.types.Material, "volume_hist_q05"):
            del bpy.types.Material.volume_hist_q05
        if hasattr(bpy.types.Material, "volume_hist_q95"):
            del bpy.types.Material.volume_hist_q95
        if hasattr(bpy.types.Material, "volume_hist_image"):
            del bpy.types.Material.volume_hist_image
        if hasattr(bpy.types.Material, "volume_hist_ready"):
            del bpy.types.Material.volume_hist_ready
        bpy.types.Material.volume_colormap = bpy.props.EnumProperty(
            name="Colormap",
            description="Colormap for the volume material",
            items=enum_colormap_items,
            default=0,
            update=_on_material_colormap_change,
        )
        bpy.types.Material.volume_colormap_reversed = bpy.props.BoolProperty(
            name="Reverse colormap",
            description="Reverse the selected colormap (like Matplotlib _r)",
            default=False,
            update=_on_material_colormap_change,
        )
        bpy.types.Material.volume_hist_vmin = bpy.props.FloatProperty(
            name="Min value",
            description="Smallest value of imported NumPy data",
            default=0.0,
            precision=6,
        )
        bpy.types.Material.volume_hist_vmax = bpy.props.FloatProperty(
            name="Max value",
            description="Largest value of imported NumPy data",
            default=1.0,
            precision=6,
        )
        bpy.types.Material.volume_hist_q05 = bpy.props.FloatProperty(
            name="5% lows",
            description="Smallest 5% of imported NumPy data",
            default=0.0,
            precision=6,
        )
        bpy.types.Material.volume_hist_q95 = bpy.props.FloatProperty(
            name="5% highs",
            description="Largest 5% of imported NumPy data",
            default=1.0,
            precision=6,
        )
        bpy.types.Material.volume_hist_image = bpy.props.PointerProperty(
            name="Histogram",
            type=bpy.types.Image,
            description="Histogram preview image",
        )
        bpy.types.Material.volume_hist_ready = bpy.props.BoolProperty(
            name="Histogram Ready",
            description="True if histogram comes from NumPy import",
            default=False,
        )

    @staticmethod
    def unregister():
        if hasattr(bpy.types.Material, "volume_hist_ready"):
            del bpy.types.Material.volume_hist_ready
        if hasattr(bpy.types.Material, "volume_hist_image"):
            del bpy.types.Material.volume_hist_image
        if hasattr(bpy.types.Material, "volume_hist_q95"):
            del bpy.types.Material.volume_hist_q95
        if hasattr(bpy.types.Material, "volume_hist_q05"):
            del bpy.types.Material.volume_hist_q05
        if hasattr(bpy.types.Material, "volume_hist_vmax"):
            del bpy.types.Material.volume_hist_vmax
        if hasattr(bpy.types.Material, "volume_hist_vmin"):
            del bpy.types.Material.volume_hist_vmin
        if hasattr(bpy.types.Material, "volume_colormap_reversed"):
            del bpy.types.Material.volume_colormap_reversed
        if hasattr(bpy.types.Material, "volume_colormap"):
            del bpy.types.Material.volume_colormap


class SciBlend_Latex_Props(bpy.types.PropertyGroup):
    latex_code: bpy.props.StringProperty(
        name="LaTeX",
        description="Enter LaTeX code surrounded with $...$",
        default="",
    )

    custom_latex_path: bpy.props.StringProperty(
        name="latex",
        description="""
        Enter the path of the folder containing the latex command
        on your computer. If you are not sure where the latex command is
        located, open your terminal/command prompt and type: \"where latex\" """,
        default="",
        update=lambda s, c: _rel_to_abs("custom_latex_path"),
        subtype="DIR_PATH",
    )

    custom_pdflatex_path: bpy.props.StringProperty(
        name="pdflatex",
        description="""
        Enter the path of the folder containing the pdflatex command
        on your computer. If you are not sure where the pdflatex command is
        located, open your terminal/command prompt and type: \"where pdflatex\" """,
        default="",
        update=lambda s, c: _rel_to_abs("custom_pdflatex_path"),
        subtype="DIR_PATH",
    )

    custom_xelatex_path: bpy.props.StringProperty(
        name="xelatex",
        description="""
        Enter the path of the folder containing the xelatex command
        on your computer. If you are not sure where the xelatex command is
        located, open your terminal/command prompt and type: \"where xelatex\" """,
        default="",
        update=lambda s, c: _rel_to_abs("custom_xelatex_path"),
        subtype="DIR_PATH",
    )

    custom_lualatex_path: bpy.props.StringProperty(
        name="lualatex",
        description="""
        Enter the path of the folder containing the lualatex command
        on your computer. If you are not sure where the lualatex command is
        located, open your terminal/command prompt and type: \"where lualatex\" """,
        default="",
        update=lambda s, c: _rel_to_abs("custom_lualatex_path"),
        subtype="DIR_PATH",
    )

    custom_dvisvgm_path: bpy.props.StringProperty(
        name="dvisvgm",
        description="""
        Enter the path of the folder containing the dvisvgm command
        on your computer. If you are not sure where the dvisvgm command is
        located, open your terminal/command prompt and type: \"where dvisvgm\" """,
        default="",
        update=lambda s, c: _rel_to_abs("custom_dvisvgm_path"),
        subtype="DIR_PATH",
    )

    command_selection: bpy.props.EnumProperty(
        name="Command",
        description="Select the command used to compile LaTeX code",
        items=[
            ("latex", "latex", "Use latex command to compile code"),
            ("pdflatex", "pdflatex", "Use pdflatex command to compile code"),
            ("xelatex", "xelatex", "Use xelatex command to compile code"),
            ("lualatex", "lualatex", "Use lualatex command to compile code"),
        ],
    )

    text_thickness: bpy.props.FloatProperty(
        name="Thickness",
        description="Set thickness of text",
        default=0.025,
    )

    text_scale: bpy.props.FloatProperty(
        name="Scale",
        description="Set size of text",
        default=1.0,
    )

    x_loc: bpy.props.FloatProperty(
        name="X",
        description="Set x position",
        default=0.0,
    )

    y_loc: bpy.props.FloatProperty(
        name="Y",
        description="Set y position",
        default=0.0,
    )

    z_loc: bpy.props.FloatProperty(
        name="Z",
        description="Set z position",
        default=0.0,
    )

    x_rot: bpy.props.FloatProperty(
        name="X",
        description="Set x rotation",
        default=0.0,
    )

    y_rot: bpy.props.FloatProperty(
        name="Y",
        description="Set y rotation",
        default=0.0,
    )

    z_rot: bpy.props.FloatProperty(
        name="Z",
        description="Set z rotation",
        default=0.0,
    )

    custom_material_bool: bpy.props.BoolProperty(
        name="Use Custom Material", description="Use a custom material", default=False
    )

    custom_material_value: bpy.props.PointerProperty(
        type=bpy.types.Material, name="Material", description="Choose a material"
    )

    custom_preamble_bool: bpy.props.BoolProperty(
        name="Use Custom Preamble", description="Use a custom preamble", default=False
    )

    preamble_path: bpy.props.StringProperty(
        name="Preamble",
        description="Choose a .tex file for the preamble",
        default="",
        update=lambda s, c: _rel_to_abs("preamble_path"),
        subtype="FILE_PATH",
    )


# -----------------------------
# Operators
# -----------------------------
class SciBlend_Tools_SwitchToCycles(bpy.types.Operator):
    bl_idname = "sci_blend.switch_to_cycles"
    bl_label = "Switch to Cycles"
    bl_description = "Switch render engine to Cycles"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.render.engine = "CYCLES"
        if (
            bpy.context.preferences.addons["cycles"].preferences.compute_device_type
            != "NONE"
        ):
            context.scene.cycles.device = "GPU"
        return {"FINISHED"}


class SciBlend_Tools_FixColors(bpy.types.Operator):
    bl_idname = "sci_blend.fix_colors"
    bl_label = "Fix Colors"
    bl_description = "Fix color management settings for scientific visualization"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        scene.view_settings.view_transform = "Standard"
        return {"FINISHED"}


class SciBlend_Tools_SetBackground(bpy.types.Operator):
    bl_idname = "sci_blend.tools_set_background"
    bl_label = "Set Background Color"
    bl_description = "Set background color for the scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.sci_blend_tools
        color = props.background_color
        world = bpy.context.scene.world
        if world is None:
            world = bpy.data.worlds.new("World")
            bpy.context.scene.world = world
        world.use_nodes = True
        bg_node = world.node_tree.nodes.get("Background")
        if bg_node is not None:
            bg_node.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
        return {"FINISHED"}


class SciBlend_Latex_CompileAsMesh(bpy.types.Operator):
    bl_idname = "sci_blend.latex_compile_as_mesh"
    bl_label = "Compile LaTeX as mesh"

    def execute(self, context):
        props = context.scene.sci_blend_latex
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
                _compile_with_latex(
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


class SciBlend_Latex_CompileAsGreasePencil(bpy.types.Operator):
    bl_idname = "sci_blend.latex_compile_as_grease_pencil"
    bl_label = "Compile LaTeX as grease pencil"

    def execute(self, context):
        props = context.scene.sci_blend_latex
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
                _compile_with_latex(
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


class SciBlend_VolumeRender_ImportVDB(bpy.types.Operator):
    bl_idname = "sci_blend.volume_render_import_vdb"
    bl_label = "Import .vdb as volume"
    bl_description = "Import a .vdb file and create a volume object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scn = context.scene
        props = scn.sci_blend_volume_render

        if not props.vdb_path:
            self.report({"ERROR"}, "Please pick a valid .vdb file first.")
            return {"CANCELLED"}

        abspath = bpy.path.abspath(props.vdb_path)
        if not os.path.exists(abspath):
            self.report({"ERROR"}, f"File not found:\n{abspath}")
            return {"CANCELLED"}

        store_path = bpy.path.relpath(abspath) if props.save_relative else abspath
        uuid_str = f"{props.static_uuid:04d}"
        props.static_uuid += 1
        _, display_name, mat = _create_volume_object(context, store_path, abspath, uuid_str)

        if mat is not None:
            _clear_histogram_on_material(mat)

        self.report({"INFO"}, f"Created Volume from .vdb file: {display_name}")
        return {"FINISHED"}


class SciBlend_VolumeRender_ImportNumpy(bpy.types.Operator):
    bl_idname = "sci_blend.volume_render_import_numpy"
    bl_label = "Import .npy/.npz as volume"
    bl_description = (
        "Load a 3D NumPy array (.npy/.npz) and create a Volume object via OpenVDB"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        import os

        def _compute_histogram_np(arr: np.ndarray, bins: int = 128):
            """
            Returns (hist: np.ndarray[int], q05: float, q95: float, vmin: float, vmax: float).
            Uses full range [min, max] for the histogram, and rough numpy quantiles for 5/95%.
            Assumes arr is already finite and float.
            """
            flat = arr.astype(np.float64, copy=False).ravel()
            if flat.size == 0:
                return np.zeros(bins, dtype=np.int32), 0.0, 0.0, 0.0, 1.0

            vmin = float(flat.min())
            vmax = float(flat.max())

            if vmax == vmin:
                vmax = vmin + 1e-12
            cnt, bns = np.histogram(flat, bins=bins, range=(vmin, vmax))
            bns = 0.5 * (bns[1:] + bns[:-1])
            cumsum = np.cumsum(cnt)
            imin = np.argmin(
                np.abs(cumsum - 0.05 * (cumsum[-1] - cumsum[0]) - cumsum[0])
            )
            imax = np.argmin(
                np.abs(cumsum - 0.95 * (cumsum[-1] - cumsum[0]) - cumsum[0])
            )
            q05, q95 = bns[imin], bns[imax]
            return cnt.astype(np.int32, copy=False), float(q05), float(q95), vmin, vmax

        props = context.scene.sci_blend_volume_render
        path = bpy.path.abspath(props.numpy_path or "")
        if not path or not os.path.exists(path):
            self.report({"ERROR"}, "Pick a valid .npy /.npz file first.")
            return {"CANCELLED"}

        directory = os.path.dirname(path)
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".npy":
                arr = np.load(path, allow_pickle=False)
            elif ext == ".npz":
                z = np.load(path, allow_pickle=False)
                key = props.npz_key.strip()
                if not key:
                    self.report(
                        {"ERROR"}, f"NPZ datasets: {list(z.files)} — set 'NPZ field'."
                    )
                    return {"CANCELLED"}
                if key not in z.files:
                    self.report(
                        {"ERROR"}, f"'{key}' not in NPZ datasets: {list(z.files)}"
                    )
                    return {"CANCELLED"}
                arr = z[key]
            else:
                self.report({"ERROR"}, "File must be .npy or .npz")
                return {"CANCELLED"}
        except Exception as e:
            self.report({"ERROR"}, f"Failed to load array: {e}")
            return {"CANCELLED"}

        if arr.ndim == 2:
            arr = arr[None, ...]  # treat as single slice: Z=1
        if arr.ndim != 3:
            self.report({"ERROR"}, f"Array must be 3D (got shape {arr.shape})")
            return {"CANCELLED"}

        # crop
        zmin = props.numpy_crop_zmin
        zmax = props.numpy_crop_zmax
        ymin = props.numpy_crop_ymin
        ymax = props.numpy_crop_ymax
        xmin = props.numpy_crop_xmin
        xmax = props.numpy_crop_xmax
        self.report(
            {"INFO"}, f"Cropping to Z[{zmin}:{zmax}] Y[{ymin}:{ymax}] X[{xmin}:{xmax}]"
        )
        try:
            arr = arr[xmin:xmax, ymin:ymax, zmin:zmax]
        except Exception as e:
            self.report({"ERROR"}, f"Invalid crop indices: {e}")
            return {"CANCELLED"}
        if arr.size == 0:
            self.report({"ERROR"}, "Cropped array is empty.")
            return {"CANCELLED"}

        order_map = {
            "ZYX": (0, 1, 2),
            "XYZ": (2, 1, 0),
            "YZX": (1, 2, 0),
            "ZXY": (0, 2, 1),
            "XZY": (2, 0, 1),
            "YXZ": (1, 0, 2),
        }
        axes = order_map.get(props.numpy_axis_order, (0, 1, 2))
        arr = np.transpose(arr, axes).astype(np.float64, copy=False)
        arr = np.nan_to_num(arr, copy=False, nan=0.0, posinf=0.0, neginf=0.0)

        _hist, _q05, _q95, _vmin, _vmax = _compute_histogram_np(arr, bins=128)

        try:
            try:
                import pyopenvdb as vdb  # type: ignore
            except Exception:
                import openvdb as vdb  # type: ignore
        except Exception:
            self.report(
                {"ERROR"},
                "pyopenvdb is not installed in Blender's Python. "
                "Install into Blender's Python and try again.",
            )
            return {"CANCELLED"}

        grid = vdb.DoubleGrid()
        grid.name = "density"
        grid.copyFromArray(arr)

        # Output file under same directory in 'sciblend_cache'
        uuid_str = f"{props.static_uuid:04d}"
        props.static_uuid += 1
        blend_dir = (
            directory if os.path.isabs(path) else os.path.dirname(bpy.data.filepath)
        )
        cache_dir = os.path.join(blend_dir, "sciblend_cache")
        os.makedirs(cache_dir, exist_ok=True)
        if ext == ".npz":
            base = os.path.splitext(os.path.basename(path))[0]
            if props.npz_key.strip():
                base += f"_{props.npz_key.strip()}"
        else:
            base = os.path.splitext(os.path.basename(path))[0]
        vdb_path = os.path.join(cache_dir, f"{base}_{uuid_str}.vdb")
        try:
            vdb.write(vdb_path, grids=[grid])
        except Exception as e:
            self.report({"ERROR"}, f"Failed to write VDB: {e}")
            return {"CANCELLED"}

        store_path = bpy.path.relpath(vdb_path) if props.save_relative else vdb_path
        vol_name, _, mat = _create_volume_object(
            context, store_path, vdb_path, uuid_str
        )

        if mat is not None:
            _store_histogram_on_material(mat, _hist, _vmin, _vmax, _q05, _q95)

        self.report(
            {"INFO"},
            f"Imported array as Volume: {vol_name}  (VDB: {os.path.basename(vdb_path)})",
        )
        return {"FINISHED"}


class SciBlend_Materials_ReverseVolumeColormap(bpy.types.Operator):
    bl_idname = "sci_blend.materials_reverse_volume_colormap"
    bl_label = "Reverse colormap"
    bl_description = "Reverse the active material's colormap"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        mat = getattr(context.object, "active_material", None)
        if mat is None:
            self.report({"ERROR"}, "No active material on the selected object.")
            return {"CANCELLED"}
        mat.volume_colormap_reversed = not bool(
            getattr(mat, "volume_colormap_reversed", False)
        )
        _on_material_colormap_change(mat, context)
        self.report({"INFO"}, f"Colormap reversed: {mat.volume_colormap_reversed}")
        return {"FINISHED"}


class SciBlend_Materials_CreateOrResetVolumeMaterial(bpy.types.Operator):
    bl_idname = "sci_blend.materials_create_or_reset_volume_material"
    bl_label = "Create or Reset Volume Material"
    bl_description = (
        "Create a basic material for volume rendering or reset the existing one"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        mat = getattr(context.object, "active_material", None)
        if mat is None:
            self.report({"ERROR"}, "No active material on the selected object.")
            return {"CANCELLED"}
        _create_or_reset_volume_material(mat.name)
        self.report({"INFO"}, f"Volume material nodes ready on '{mat.name}'.")
        return {"FINISHED"}


# -----------------------------
# UI Panels
# -----------------------------
class SciBlend_Material_NDE_UI(bpy.types.Panel):
    bl_label = "Volume material"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "SciBlend"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        obj = context.object
        return (
            space is not None
            and getattr(space, "tree_type", "") == "ShaderNodeTree"
            and obj is not None
            and obj.active_material is not None
        )

    def draw(self, context):
        layout = self.layout
        mat = context.object.active_material

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.row().operator(
            "sci_blend.materials_create_or_reset_volume_material",
            icon="NODETREE",
            text="Create/reset volume material",
        )
        layout.separator()

        box = layout.box()
        box.row().label(text="Colormap", icon="COLOR")
        box.row().template_icon_view(mat, "volume_colormap", show_labels=True, scale=5)

        box.row().operator(
            "sci_blend.materials_reverse_volume_colormap",
            icon="ARROW_LEFTRIGHT",
            text="Reverse colormap",
        )

        if getattr(mat, "volume_hist_ready", False) and mat.volume_hist_image:
            layout.separator()
            box = layout.box()
            box.row().label(text="Value ranges", icon="UV_DATA")

            split = box.split()
            col = split.column(align=True)
            col.row().label(text="min/max")
            col.row().label(text=f"min: {mat.volume_hist_vmin:.3g}")
            col.row().label(text=f"max: {mat.volume_hist_vmax:.3g}")
            col = split.column(align=True)
            col.row().label(text="5% quantiles")
            col.row().label(text=f"min: {mat.volume_hist_q05:.3g}")
            col.row().label(text=f"max: {mat.volume_hist_q95:.3g}")

            box.row().label(text="Histogram", icon="GRAPH")
            row = box.row()
            row.ui_units_x = 24
            row.scale_x = 10
            row.scale_y = 10
            icon_id = mat.volume_hist_image.preview.icon_id
            row.template_icon(icon_value=icon_id)
            box.row().label(text="Quantiles shown with red lines", icon="INFO")


class SciBlend_Tools_3DV_UI(bpy.types.Panel):
    bl_label = "Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SciBlend"

    def draw(self, context):
        layout = self.layout
        props = context.scene.sci_blend_tools

        layout.separator()
        box = layout.box()
        box.row().label(
            text="Enable CUDA/HIP/OneAPI support in Preferences before proceeding.",
            icon="INFO",
        )
        box.row().operator("sci_blend.switch_to_cycles", icon="RENDER_STILL")
        box.row().operator("sci_blend.fix_colors", icon="COLOR")

        layout.separator()
        box = layout.box()
        box.row().prop(props, "background_color")
        box.row().operator("sci_blend.tools_set_background", icon="WORLD")


class SciBlend_VolumeRender_3DV_UI(bpy.types.Panel):
    bl_label = "Volume Rendering"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SciBlend"

    def draw(self, context):
        layout = self.layout
        props = context.scene.sci_blend_volume_render

        layout.prop(props, "save_relative")

        layout.separator()

        box = layout.box()
        box.row().label(text="VDB → Volume (.vdb)")
        box.row().prop(props, "vdb_path")
        box.row().operator("sci_blend.volume_render_import_vdb", icon="IMPORT")

        layout.separator()
        box = layout.box()
        box.row().label(text="NumPy → Volume (.npy / .npz)")
        box.row().prop(props, "numpy_path")
        box.row().prop(props, "npz_key")
        box.row().prop(props, "numpy_axis_order")
        box_crop = box.box()
        box_crop.label(text="Crop indices")
        row = box_crop.row()
        split = row.split()
        split.column().prop(props, "numpy_crop_xmin")
        split.column().prop(props, "numpy_crop_xmax")
        row = box_crop.row()
        split = row.split()
        split.column().prop(props, "numpy_crop_ymin")
        split.column().prop(props, "numpy_crop_ymax")
        row = box_crop.row()
        split = row.split()
        split.column().prop(props, "numpy_crop_zmin")
        split.column().prop(props, "numpy_crop_zmax")
        box.row().operator("sci_blend.volume_render_import_numpy", icon="IMPORT")


class SciBlend_Latex_3DV_UI(bpy.types.Panel):
    bl_label = "Latex"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SciBlend"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        props = context.scene.sci_blend_latex

        layout.label(text="Adapted from ghseeli/latex2blender", icon="INFO")
        layout.separator()

        layout.prop(props, "latex_code")
        layout.separator()

        layout.prop(props, "command_selection")
        layout.separator

        box = layout.box()
        box.label(text="Paths to directories containing commands.")
        box.label(
            text="If the plugin is unable to find the commands, set them here.",
            icon="INFO",
        )
        box.row().prop(props, "custom_latex_path")
        box.row().prop(props, "custom_pdflatex_path")
        box.row().prop(props, "custom_xelatex_path")
        box.row().prop(props, "custom_lualatex_path")
        box.row().prop(props, "custom_dvisvgm_path")

        box = layout.box()
        box.label(text="Transform Settings")
        box.row().prop(props, "text_scale")
        box.row().prop(props, "text_thickness")

        split = box.split()

        col = split.column(align=True)
        col.label(text="Location:")
        col.prop(props, "x_loc")
        col.prop(props, "y_loc")
        col.prop(props, "z_loc")

        col = split.column(align=True)
        col.label(text="Rotation:")
        col.prop(props, "x_rot")
        col.prop(props, "y_rot")
        col.prop(props, "z_rot")

        layout.prop(props, "custom_preamble_bool")
        if props.custom_preamble_bool:
            layout.prop(props, "preamble_path")

        layout.prop(props, "custom_material_bool")
        if props.custom_material_bool:
            layout.prop(props, "custom_material_value")

        layout.separator()

        box = layout.box()
        row = box.row()
        row.operator("sci_blend.latex_compile_as_mesh", icon="MESH_CUBE")
        row = box.row()
        row.operator("sci_blend.latex_compile_as_grease_pencil", icon="GREASEPENCIL")


# -----------------------------
classes = (
    # props
    SciBlend_Tools_Props,
    SciBlend_VolumeRender_Props,
    SciBlend_Latex_Props,
    # operators
    SciBlend_Materials_ReverseVolumeColormap,
    SciBlend_Materials_CreateOrResetVolumeMaterial,
    SciBlend_Latex_CompileAsMesh,
    SciBlend_Latex_CompileAsGreasePencil,
    SciBlend_Tools_FixColors,
    SciBlend_Tools_SwitchToCycles,
    SciBlend_Tools_SetBackground,
    SciBlend_VolumeRender_ImportVDB,
    SciBlend_VolumeRender_ImportNumpy,
    # panels
    SciBlend_Material_NDE_UI,
    SciBlend_Tools_3DV_UI,
    SciBlend_VolumeRender_3DV_UI,
    SciBlend_Latex_3DV_UI,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    _build_colormap_previews()
    SciBlend_Material_Props.register()

    bpy.types.Scene.sci_blend_tools = bpy.props.PointerProperty(
        type=SciBlend_Tools_Props
    )
    bpy.types.Scene.sci_blend_volume_render = bpy.props.PointerProperty(
        type=SciBlend_VolumeRender_Props
    )
    bpy.types.Scene.sci_blend_latex = bpy.props.PointerProperty(
        type=SciBlend_Latex_Props
    )


def unregister():
    del bpy.types.Scene.sci_blend_tools
    del bpy.types.Scene.sci_blend_volume_render
    del bpy.types.Scene.sci_blend_latex
    SciBlend_Material_Props.unregister()
    _free_colormap_previews()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
