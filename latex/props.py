import bpy  # type: ignore

from .utils import Rel_to_abs

class Latex_Props(bpy.types.PropertyGroup):
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
        update=lambda s, c: Rel_to_abs("custom_latex_path"),
        subtype="DIR_PATH",
    )

    custom_pdflatex_path: bpy.props.StringProperty(
        name="pdflatex",
        description="""
        Enter the path of the folder containing the pdflatex command
        on your computer. If you are not sure where the pdflatex command is
        located, open your terminal/command prompt and type: \"where pdflatex\" """,
        default="",
        update=lambda s, c: Rel_to_abs("custom_pdflatex_path"),
        subtype="DIR_PATH",
    )

    custom_xelatex_path: bpy.props.StringProperty(
        name="xelatex",
        description="""
        Enter the path of the folder containing the xelatex command
        on your computer. If you are not sure where the xelatex command is
        located, open your terminal/command prompt and type: \"where xelatex\" """,
        default="",
        update=lambda s, c: Rel_to_abs("custom_xelatex_path"),
        subtype="DIR_PATH",
    )

    custom_lualatex_path: bpy.props.StringProperty(
        name="lualatex",
        description="""
        Enter the path of the folder containing the lualatex command
        on your computer. If you are not sure where the lualatex command is
        located, open your terminal/command prompt and type: \"where lualatex\" """,
        default="",
        update=lambda s, c: Rel_to_abs("custom_lualatex_path"),
        subtype="DIR_PATH",
    )

    custom_dvisvgm_path: bpy.props.StringProperty(
        name="dvisvgm",
        description="""
        Enter the path of the folder containing the dvisvgm command
        on your computer. If you are not sure where the dvisvgm command is
        located, open your terminal/command prompt and type: \"where dvisvgm\" """,
        default="",
        update=lambda s, c: Rel_to_abs("custom_dvisvgm_path"),
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
        update=lambda s, c: Rel_to_abs("preamble_path"),
        subtype="FILE_PATH",
    )

