import bpy

from ..colormaps.data import (  # pyright: ignore[reportMissingImports]
    Resolve_cmap_id,
    Stops_for_colormap,
    Apply_stops_to_colorramp,
)

from ..utilities.nodes import CreateNodes  # pyright: ignore[reportMissingImports]
from ..utilities.materials import (  # pyright: ignore[reportMissingImports]
    CommonMaterialColormapChange,
)


def Create_fieldline_geometry(
    context: bpy.types.Context,
    raw_collection: bpy.types.Collection | None = None,
    material: bpy.types.Material | None = None,
    uuid_str: str = "",
) -> bpy.types.Object:
    suffix = f"_{uuid_str}" if uuid_str != "" else ""

    bpy.ops.object.volume_add(align="WORLD")
    obj = context.active_object
    if obj is None:
        raise RuntimeError("Failed to create empty object")
    obj.name = f"FieldlineGeometry{suffix}"

    nt = bpy.data.node_groups.new(
        type="GeometryNodeTree", name=f"FieldlineGeometryNodes{suffix}"
    )
    obj.modifiers.new(name="GeometryNodes", type="NODES")
    obj.modifiers["GeometryNodes"].node_group = nt

    def _modify_capture_attribute(n):
        n.capture_items.clear()
        n.capture_items.new("FLOAT", "Index")
        n.capture_items["Index"].data_type = "INT"

    def _modify_modulate_switch(n):
        n.inputs[1].default_value = 1.0

    CreateNodes(
        node_kwargs=[
            [
                {
                    "type_id": "GeometryNodeCollectionInfo",
                    "label": "Raw Fieldlines",
                    "input_defaults": {
                        "Separate Children": True,
                        0: raw_collection,
                    },
                },
                {
                    "type_id": "GeometryNodeInputIndex",
                    "label": "Fieldline Index",
                },
            ],
            [
                {
                    "type_id": "GeometryNodeCaptureAttribute",
                    "label": "Capture Fieldline Index",
                    "domain": "INSTANCE",
                    "extra": _modify_capture_attribute,
                }
            ],
            [
                {
                    "type_id": "GeometryNodeRealizeInstances",
                    "label": "Realize Fieldlines",
                },
                {
                    "type_id": "GeometryNodeInputIndex",
                    "label": "Point Index",
                },
            ],
            [
                {
                    "type_id": "GeometryNodeInputNamedAttribute",
                    "label": f"Attr {xyzt.upper()}",
                    "data_type": "FLOAT",
                    "input_defaults": {0: xyzt},
                }
                for xyzt in ["x", "y", "z", "thickness", "color"]
            ],
            [
                {
                    "type_id": "GeometryNodeSampleIndex",
                    "label": f"Sample {xyzt.upper()}",
                    "domain": "POINT",
                    "data_type": "FLOAT",
                }
                for xyzt in ["x", "y", "z", "thickness", "color"]
            ],
            [
                {
                    "type_id": "ShaderNodeCombineXYZ",
                    "label": "Combine XYZ",
                }
            ],
            [{"type_id": "GeometryNodeSetPosition", "label": "Point Positions"}],
            [
                {
                    "type_id": "GeometryNodeMeshToPoints",
                    "label": "Convert To Points",
                    "mode": "VERTICES",
                },
                {
                    "type_id": "NodeGroupInput",
                    "label": "Group Input",
                },
            ],
            [
                {
                    "type_id": "GeometryNodePointsToCurves",
                    "label": "Points To Curves",
                },
                {
                    "type_id": "GeometryNodeSwitch",
                    "label": "Modulate Thickness",
                    "input_type": "FLOAT",
                    "extra": _modify_modulate_switch,
                },
            ],
            [
                {
                    "type_id": "GeometryNodeStoreNamedAttribute",
                    "label": "Store Color",
                    "data_type": "FLOAT",
                    "domain": "POINT",
                    "input_defaults": {2: "color_modulate"},
                },
                {
                    "type_id": "GeometryNodeCurvePrimitiveCircle",
                    "label": "Circle Profile",
                    "mode": "RADIUS",
                },
            ],
            [
                {
                    "type_id": "GeometryNodeCurveToMesh",
                    "label": "Curves To Mesh",
                    "input_defaults": {"Fill Caps": True, "Scale": 1.0},
                },
            ],
            [
                {
                    "type_id": "GeometryNodeSetMaterial",
                    "label": "Set Material",
                    "input_defaults": {"Material": material},
                },
            ],
            [
                {
                    "type_id": "NodeGroupOutput",
                    "label": "Group Output",
                    "is_active_output": True,
                },
            ],
        ],
        socket_kwargs=[
            {"name": "Geometry", "in_out": "OUTPUT", "type": "NodeSocketGeometry"},
            {
                "name": "Resolution",
                "in_out": "INPUT",
                "type": "NodeSocketInt",
                "min_value": 3,
                "max_value": 64,
                "description": "Circle profile resolution",
            },
            {
                "name": "Radius",
                "in_out": "INPUT",
                "type": "NodeSocketFloat",
                "min_value": 0.0,
                "max_value": 3.4028234663852886e38,
                "subtype": "DISTANCE",
                "description": "Circle profile maximum radius",
            },
            {
                "name": "Modulate Thickness",
                "in_out": "INPUT",
                "type": "NodeSocketBool",
                "description": "Enable or disable thickness modulation",
            },
        ],
        node_links=[
            (("RawFieldlines", "Instances"), ("CaptureFieldlineIndex", "Geometry")),
            (("FieldlineIndex", "Index"), ("CaptureFieldlineIndex", "Index")),
            (("CaptureFieldlineIndex", "Geometry"), ("RealizeFieldlines", "Geometry")),
            (("RealizeFieldlines", "Geometry"), ("PointPositions", "Geometry")),
            (("RealizeFieldlines", "Geometry"), ("SampleX", "Geometry")),
            (("RealizeFieldlines", "Geometry"), ("SampleY", "Geometry")),
            (("RealizeFieldlines", "Geometry"), ("SampleZ", "Geometry")),
            (("RealizeFieldlines", "Geometry"), ("SampleTHICKNESS", "Geometry")),
            (("RealizeFieldlines", "Geometry"), ("SampleCOLOR", "Geometry")),
            (("AttrX", "Attribute"), ("SampleX", "Value")),
            (("AttrY", "Attribute"), ("SampleY", "Value")),
            (("AttrZ", "Attribute"), ("SampleZ", "Value")),
            (("AttrTHICKNESS", "Attribute"), ("SampleTHICKNESS", "Value")),
            (("AttrCOLOR", "Attribute"), ("SampleCOLOR", "Value")),
            (("PointIndex", "Index"), ("SampleX", "Index")),
            (("PointIndex", "Index"), ("SampleY", "Index")),
            (("PointIndex", "Index"), ("SampleZ", "Index")),
            (("PointIndex", "Index"), ("SampleTHICKNESS", "Index")),
            (("PointIndex", "Index"), ("SampleCOLOR", "Index")),
            (("SampleX", "Value"), ("CombineXYZ", "X")),
            (("SampleY", "Value"), ("CombineXYZ", "Y")),
            (("SampleZ", "Value"), ("CombineXYZ", "Z")),
            (("SampleTHICKNESS", "Value"), ("ModulateThickness", "True")),
            (("SampleCOLOR", "Value"), ("StoreColor", "Value")),
            (("ModulateThickness", "Output"), ("CurvesToMesh", "Scale")),
            (("CombineXYZ", "Vector"), ("PointPositions", "Position")),
            (("PointPositions", "Geometry"), ("ConvertToPoints", "Mesh")),
            (("ConvertToPoints", "Points"), ("PointsToCurves", "Points")),
            (("CaptureFieldlineIndex", "Index"), ("PointsToCurves", "Curve Group ID")),
            (("PointsToCurves", "Curves"), ("StoreColor", "Geometry")),
            (("StoreColor", "Geometry"), ("CurvesToMesh", "Curve")),
            (("GroupInput", "Resolution"), ("CircleProfile", "Resolution")),
            (("GroupInput", "Radius"), ("CircleProfile", "Radius")),
            (("GroupInput", "Modulate Thickness"), ("ModulateThickness", "Switch")),
            (("CircleProfile", "Curve"), ("CurvesToMesh", "Profile Curve")),
            (("CurvesToMesh", "Mesh"), ("SetMaterial", "Geometry")),
            (("SetMaterial", "Geometry"), ("GroupOutput", "Geometry")),
        ],
        node_tree=nt,
        clear=True,
    )
    obj.modifiers["GeometryNodes"]["Socket_1"] = 8
    obj.modifiers["GeometryNodes"]["Socket_2"] = 0.5
    obj.modifiers["GeometryNodes"]["Socket_3"] = True

    return obj


def Create_or_reset_fieldline_material(name: str):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        if (nt := mat.node_tree) is None:
            raise RuntimeError("Failed to create node tree for new material")
        nt.nodes.clear()
    else:
        if not mat.use_nodes:
            mat.use_nodes = True

    if mat.node_tree is None:
        raise RuntimeError("Failed to access node tree of material")

    nodes = CreateNodes(
        node_kwargs=[
            [
                {
                    "type_id": "ShaderNodeAttribute",
                    "label": "Geometry Attribute",
                    "attribute_name": "color_modulate",
                },
            ],
            [
                {
                    "type_id": "ShaderNodeValToRGB",
                    "label": "Colormap",
                    "width": 2,
                }
            ],
            [
                {
                    "type_id": "ShaderNodeBsdfPrincipled",
                    "label": "Principled BSDF",
                    "input_defaults": {"Roughness": 1.0, "Emission Strength": 0.25},
                    "width": 2,
                }
            ],
            [
                {
                    "type_id": "ShaderNodeOutputMaterial",
                    "label": "Material Output",
                    "is_active_output": True,
                }
            ],
        ],
        socket_kwargs=[],
        node_links=[
            (("GeometryAttribute", "Fac"), ("Colormap", "Fac")),
            (("Colormap", "Color"), ("PrincipledBSDF", "Base Color")),
            (("Colormap", "Color"), ("PrincipledBSDF", "Emission Color")),
            (("PrincipledBSDF", "BSDF"), ("MaterialOutput", "Surface")),
        ],
        node_tree=mat.node_tree,
        clear=False,
    )

    cm_id = Resolve_cmap_id(getattr(mat, "fieldline_colormap", 0))
    rev = bool(getattr(mat, "fieldline_colormap_reversed", False))
    Apply_stops_to_colorramp(
        nodes["Colormap"].color_ramp, Stops_for_colormap(cm_id, reverse=rev)
    )

    return mat


def On_material_colormap_change(self, _: bpy.types.Context):
    """Update callback: self is the Material that owns 'fieldline_colormap'."""
    if not getattr(self, "use_nodes", False) or not self.node_tree:
        return None
    CommonMaterialColormapChange(
        cmap_attr=getattr(self, "fieldline_colormap", 0),
        cmap_reversed_attr=bool(getattr(self, "fieldline_colormap_reversed", False)),
        name=self.name,
        create_or_reset_callback=Create_or_reset_fieldline_material,
        nt=self.node_tree,
    )
