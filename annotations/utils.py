from typing import Any
import bpy
from numpy import empty

from ..utilities.nodes import CreateNodes  # pyright: ignore[reportMissingImports]


def Add_simple_material_to_object(
    obj: bpy.types.Object,
    name: str,
    bsdf_props: dict[str, Any] = {},
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    if mat.node_tree is None:
        raise ValueError("Node Tree not activated")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")

    if bsdf is None or bsdf.inputs is None:
        raise ValueError("Failed to get BSDF inputs")

    for prop, value in bsdf_props.items():
        if prop in bsdf.inputs:
            bsdf.inputs[prop].default_value = value

    if obj.data is None:
        raise ValueError("Failed to get object data")

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    return mat


def Axes_grid_geometry_node(
    mat: bpy.types.Material | None = None,
) -> bpy.types.NodeTree:
    def divider_node_group():
        divider = bpy.data.node_groups.new(type="GeometryNodeTree", name="Divider")
        CreateNodes(
            node_kwargs=[
                [
                    {
                        "type_id": "NodeGroupInput",
                        "label": "Group Input",
                    }
                ],
                [
                    {
                        "type_id": "ShaderNodeMath",
                        "label": "Size/MinCutoff",
                        "operation": "DIVIDE",
                    },
                    {
                        "type_id": "ShaderNodeMath",
                        "label": "MAX(Size/MinCutoff|Delta)",
                        "operation": "MAXIMUM",
                    },
                ],
                [
                    {
                        "type_id": "ShaderNodeMath",
                        "label": "Size/DeltaMin",
                        "operation": "DIVIDE",
                    },
                ],
                [
                    {
                        "type_id": "ShaderNodeMath",
                        "label": "Floor(Npoints)",
                        "operation": "FLOOR",
                    },
                    {
                        "type_id": "ShaderNodeMath",
                        "label": "Floor(Npoints)*Delta",
                        "operation": "MULTIPLY",
                    },
                    {
                        "type_id": "ShaderNodeMath",
                        "label": "Remainder",
                        "operation": "SUBTRACT",
                    },
                ],
                [
                    {
                        "type_id": "NodeGroupOutput",
                        "label": "Group Output",
                        "is_active_output": True,
                    }
                ],
            ],
            socket_kwargs=[
                {
                    "name": "Size",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Delta",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "MinCutoff",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                    "default_value": 1000.0,
                    "min_value": 1.0,
                    "max_value": 1e4,
                },
                {
                    "name": "IntegerPart",
                    "in_out": "OUTPUT",
                    "type": "NodeSocketInt",
                },
                {
                    "name": "Remainder",
                    "in_out": "OUTPUT",
                    "type": "NodeSocketFloat",
                },
            ],
            node_links=[
                (("GroupInput", "Size"), ("Size/MinCutoff", 0)),
                (("GroupInput", "MinCutoff"), ("Size/MinCutoff", 1)),
                (("Size/MinCutoff", "Value"), ("MAX(Size/MinCutoff|Delta)", 0)),
                (("GroupInput", "Delta"), ("MAX(Size/MinCutoff|Delta)", 1)),
                (("GroupInput", "Size"), ("Size/DeltaMin", 0)),
                (("MAX(Size/MinCutoff|Delta)", "Value"), ("Size/DeltaMin", 1)),
                (("Size/DeltaMin", "Value"), ("Floor(Npoints)", 0)),
                (("Floor(Npoints)", "Value"), ("Floor(Npoints)*Delta", 0)),
                (("GroupInput", "Delta"), ("Floor(Npoints)*Delta", 1)),
                (("GroupInput", "Size"), ("Remainder", 0)),
                (("Floor(Npoints)*Delta", "Value"), ("Remainder", 1)),
                (("Floor(Npoints)", "Value"), ("GroupOutput", "IntegerPart")),
                (("Remainder", "Value"), ("GroupOutput", "Remainder")),
            ],
            node_tree=divider,
            clear=True,
        )
        return divider

    divider = divider_node_group()

    def generate_points():
        genpoints = bpy.data.node_groups.new(
            type="GeometryNodeTree", name="GeneratePoints"
        )
        CreateNodes(
            node_kwargs=[
                [
                    {
                        "type_id": "NodeGroupInput",
                        "label": "Group Input",
                    },
                    {
                        "type_id": "GeometryNodeInputIndex",
                        "label": "Point Index",
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeGroup",
                        "label": "Divider",
                        "node_tree": divider,
                    },
                    {
                        "type_id": "ShaderNodeMath",
                        "label": "Delta*Index",
                        "operation": "MULTIPLY",
                    },
                    {
                        "type_id": "ShaderNodeCombineXYZ",
                        "label": "XOffset",
                    },
                ],
                [
                    {
                        "type_id": "FunctionNodeIntegerMath",
                        "label": "Int+1",
                        "operation": "ADD",
                        "input_defaults": {1: 1},
                    },
                    {
                        "type_id": "GeometryNodeMeshGrid",
                        "label": "Grid",
                        "input_defaults": {0: 1.0, 1: 0.0, 3: 1},
                    },
                    {
                        "type_id": "ShaderNodeCombineXYZ",
                        "label": "AnotherXOffset",
                    },
                    {
                        "type_id": "GeometryNodePoints",
                        "label": "Points",
                        "input_defaults": {0: 1},
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeMeshToPoints",
                        "label": "Mesh To Points",
                        "mode": "VERTICES",
                    },
                    {
                        "type_id": "FunctionNodeCompare",
                        "label": "GreaterThanZero",
                        "data_type": "FLOAT",
                        "mode": "ELEMENT",
                        "operation": "GREATER_THAN",
                        "input_defaults": {1: 0.0},
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeJoinGeometry",
                        "label": "Join Geometry",
                    },
                    {
                        "type_id": "GeometryNodeSwitch",
                        "label": "Switch",
                        "input_type": "GEOMETRY",
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeBoundBox",
                        "label": "Bounding Box",
                        "input_defaults": {1: False},
                    },
                    {"type_id": "ShaderNodeSeparateXYZ", "label": "Min XBound"},
                    {"type_id": "ShaderNodeSeparateXYZ", "label": "Max XBound"},
                ],
                [
                    {
                        "type_id": "NodeGroupOutput",
                        "label": "Group Output",
                        "is_active_output": True,
                    }
                ],
            ],
            socket_kwargs=[
                {
                    "name": "Size",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Delta",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Points",
                    "in_out": "OUTPUT",
                    "type": "NodeSocketGeometry",
                },
                {
                    "name": "XMin",
                    "in_out": "OUTPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "XMax",
                    "in_out": "OUTPUT",
                    "type": "NodeSocketFloat",
                },
            ],
            node_links=[
                (("GroupInput", "Size"), ("Divider", "Size")),
                (("GroupInput", "Delta"), ("Divider", "Delta")),
                (("GroupInput", "Delta"), ("Delta*Index", 0)),
                (("PointIndex", "Index"), ("Delta*Index", 1)),
                (("GroupInput", "Size"), ("XOffset", 0)),
                (("Divider", "IntegerPart"), ("Int+1", 0)),
                (("Divider", "Remainder"), ("GreaterThanZero", 0)),
                (("Delta*Index", "Value"), ("AnotherXOffset", 0)),
                (("XOffset", "Vector"), ("Points", "Position")),
                (("Int+1", "Value"), ("Grid", 2)),
                (("Grid", "Mesh"), ("MeshToPoints", "Mesh")),
                (("AnotherXOffset", "Vector"), ("MeshToPoints", "Position")),
                (("Points", "Points"), ("Switch", "True")),
                (("MeshToPoints", "Points"), ("JoinGeometry", 0)),
                (("GreaterThanZero", "Result"), ("Switch", "Switch")),
                (("JoinGeometry", 0), ("BoundingBox", "Geometry")),
                (("JoinGeometry", 0), ("GroupOutput", "Points")),
                (("Switch", "Output"), ("JoinGeometry", 0)),
                (("BoundingBox", "Min"), ("MinXBound", "Vector")),
                (("BoundingBox", "Max"), ("MaxXBound", "Vector")),
                (("MinXBound", "X"), ("GroupOutput", "XMin")),
                (("MaxXBound", "X"), ("GroupOutput", "XMax")),
            ],
            node_tree=genpoints,
            clear=True,
        )
        return genpoints

    genpoints = generate_points()

    def generate_ticks():
        genticks = bpy.data.node_groups.new(
            type="GeometryNodeTree", name="GenerateTicks"
        )
        CreateNodes(
            node_kwargs=[
                [
                    {
                        "type_id": "NodeGroupInput",
                        "label": "Group Input",
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeGroup",
                        "label": "GeneratePoints",
                        "node_tree": genpoints,
                    },
                    {
                        "type_id": "GeometryNodeCurvePrimitiveLine",
                        "label": "Curve Line",
                        "mode": "POINTS",
                        "input_defaults": {0: (0.0, 0.0, 0.0), 1: (0.0, 0.0, 1.0)},
                    },
                ],
                [
                    {
                        "type_id": "ShaderNodeCombineXYZ",
                        "label": "XMin Offset",
                    },
                    {
                        "type_id": "ShaderNodeCombineXYZ",
                        "label": "XMax Offset",
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodePoints",
                        "label": "XMin Points",
                        "input_defaults": {0: 1},
                    },
                    {
                        "type_id": "GeometryNodePoints",
                        "label": "XMax Points",
                        "input_defaults": {0: 1},
                    },
                    {
                        "type_id": "GeometryNodeInstanceOnPoints",
                        "label": "Instance On Points",
                        "input_defaults": {5: (-1.5707963705062866, 0.0, 0.0)},
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeJoinGeometry",
                        "label": "Join Geometry",
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodePointsToCurves",
                        "label": "Points To Curves",
                    },
                    {
                        "type_id": "GeometryNodeSetPosition",
                        "label": "Set Position",
                        "input_defaults": {3: (0, 1, 0)},
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeJoinGeometry",
                        "label": "Join Geometry Final",
                    },
                ],
                [
                    {
                        "type_id": "NodeGroupOutput",
                        "label": "Group Output",
                        "is_active_output": True,
                    }
                ],
            ],
            socket_kwargs=[
                {
                    "name": "Size",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Delta",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Geometry",
                    "in_out": "OUTPUT",
                    "type": "NodeSocketGeometry",
                },
            ],
            node_links=[
                (("GroupInput", "Size"), ("GeneratePoints", "Size")),
                (("GroupInput", "Delta"), ("GeneratePoints", "Delta")),
                (("GeneratePoints", "Points"), ("InstanceOnPoints", "Points")),
                (("GeneratePoints", "XMin"), ("XMinOffset", "X")),
                (("GeneratePoints", "XMax"), ("XMaxOffset", "X")),
                (("CurveLine", "Curve"), ("InstanceOnPoints", "Instance")),
                (("XMinOffset", "Vector"), ("XMinPoints", "Position")),
                (("XMaxOffset", "Vector"), ("XMaxPoints", "Position")),
                (("XMinPoints", "Points"), ("JoinGeometry", 0)),
                (("XMaxPoints", "Points"), ("JoinGeometry", 0)),
                (("InstanceOnPoints", "Instances"), ("JoinGeometryFinal", 0)),
                (("JoinGeometry", 0), ("PointsToCurves", "Points")),
                (("PointsToCurves", "Curves"), ("SetPosition", "Geometry")),
                (("PointsToCurves", "Curves"), ("JoinGeometryFinal", 0)),
                (("SetPosition", "Geometry"), ("JoinGeometryFinal", 0)),
                (("JoinGeometryFinal", 0), ("GroupOutput", "Geometry")),
            ],
            node_tree=genticks,
            clear=True,
        )
        return genticks

    genticks = generate_ticks()

    def pick_vector_component():
        pickvectorcomp = bpy.data.node_groups.new(
            type="GeometryNodeTree", name="PickVectorComponent"
        )

        CreateNodes(
            node_kwargs=[
                [
                    {
                        "type_id": "NodeGroupInput",
                        "label": "Group Input",
                    },
                ],
                [
                    {
                        "type_id": "FunctionNodeCompare",
                        "label": "Is0",
                        "data_type": "INT",
                        "mode": "ELEMENT",
                        "operation": "EQUAL",
                        "input_defaults": {3: 0},
                    },
                    {
                        "type_id": "FunctionNodeCompare",
                        "label": "Is1",
                        "data_type": "INT",
                        "mode": "ELEMENT",
                        "operation": "EQUAL",
                        "input_defaults": {3: 1},
                    },
                    {
                        "type_id": "ShaderNodeSeparateXYZ",
                        "label": "Separate XYZ",
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeSwitch",
                        "label": "SwitchIs0",
                        "input_type": "FLOAT",
                    },
                    {
                        "type_id": "GeometryNodeSwitch",
                        "label": "SwitchIs1",
                        "input_type": "FLOAT",
                    },
                ],
                [
                    {
                        "type_id": "NodeGroupOutput",
                        "label": "Group Output",
                        "is_active_output": True,
                    }
                ],
            ],
            socket_kwargs=[
                {
                    "name": "PickComponent",
                    "in_out": "INPUT",
                    "type": "NodeSocketInt",
                },
                {
                    "name": "Vector",
                    "in_out": "INPUT",
                    "type": "NodeSocketVector",
                },
                {
                    "name": "Component",
                    "in_out": "OUTPUT",
                    "type": "NodeSocketFloat",
                },
            ],
            node_links=[
                (("GroupInput", "PickComponent"), ("Is0", "A")),
                (("GroupInput", "PickComponent"), ("Is1", "A")),
                (("GroupInput", "Vector"), ("SeparateXYZ", "Vector")),
                (("Is0", "Result"), ("SwitchIs0", "Switch")),
                (("Is1", "Result"), ("SwitchIs1", "Switch")),
                (("SeparateXYZ", "X"), ("SwitchIs0", "True")),
                (("SeparateXYZ", "Y"), ("SwitchIs1", "True")),
                (("SeparateXYZ", "Z"), ("SwitchIs1", "False")),
                (("SwitchIs1", "Output"), ("SwitchIs0", "False")),
                (("SwitchIs0", "Output"), ("GroupOutput", "Component")),
            ],
            node_tree=pickvectorcomp,
            clear=True,
        )
        return pickvectorcomp

    pickvectorcomp = pick_vector_component()

    def plane_transformation():
        planetransform = bpy.data.node_groups.new(
            type="GeometryNodeTree", name="PlaneTransformation"
        )

        CreateNodes(
            node_kwargs=[
                [
                    {
                        "type_id": "NodeGroupInput",
                        "label": "Group Input",
                    },
                ],
                [
                    {
                        "type_id": "ShaderNodeCombineXYZ",
                        "label": "Generate Stretch",
                        "input_defaults": {0: 1, 2: 1},
                        "height": 0.75,
                    },
                    {
                        "type_id": "ShaderNodeVectorMath",
                        "label": "Size Translate",
                        "operation": "MULTIPLY",
                        "height": 0.75,
                    },
                    {
                        "type_id": "ShaderNodeVectorMath",
                        "label": "Rescale Rotation",
                        "operation": "MULTIPLY",
                        "input_defaults": {1: (1.5708, -1.5708, 1.5708)},
                    },
                    {
                        "type_id": "FunctionNodeEulerToRotation",
                        "label": "Generate Rotation",
                    },
                ],
                [
                    {
                        "type_id": "NodeGroupOutput",
                        "label": "Group Output",
                        "is_active_output": True,
                    }
                ],
            ],
            socket_kwargs=[
                {
                    "name": "SizeAcross",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                    "default_value": 1.0,
                },
                {
                    "name": "Sizes",
                    "in_out": "INPUT",
                    "type": "NodeSocketVector",
                },
                {
                    "name": "TranslateInXYZ",
                    "in_out": "INPUT",
                    "type": "NodeSocketVector",
                },
                {
                    "name": "RotateInXYZ",
                    "in_out": "INPUT",
                    "type": "NodeSocketVector",
                },
                {
                    "name": "Translation",
                    "in_out": "OUTPUT",
                    "type": "NodeSocketVector",
                },
                {
                    "name": "Rotation",
                    "in_out": "OUTPUT",
                    "type": "NodeSocketRotation",
                },
                {
                    "name": "Stretch",
                    "in_out": "OUTPUT",
                    "type": "NodeSocketVector",
                },
            ],
            node_links=[
                (("GroupInput", "SizeAcross"), ("GenerateStretch", 1)),
                (("GroupInput", "Sizes"), ("SizeTranslate", 0)),
                (("GroupInput", "TranslateInXYZ"), ("SizeTranslate", 1)),
                (("GroupInput", "RotateInXYZ"), ("RescaleRotation", 0)),
                (("RescaleRotation", "Vector"), ("GenerateRotation", "Euler")),
                (("GenerateStretch", "Vector"), ("GroupOutput", "Stretch")),
                (("SizeTranslate", "Vector"), ("GroupOutput", "Translation")),
                (("GenerateRotation", "Rotation"), ("GroupOutput", "Rotation")),
            ],
            node_tree=planetransform,
            clear=True,
        )

        return planetransform

    planetransform = plane_transformation()

    def generate_plane():
        plane = bpy.data.node_groups.new(type="GeometryNodeTree", name="Plane")

        CreateNodes(
            node_kwargs=[
                [
                    {
                        "type_id": "NodeGroupInput",
                        "label": "Group Input",
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeGroup",
                        "label": "Pick SideAlong SizeX",
                        "node_tree": pickvectorcomp,
                    },
                    {
                        "type_id": "GeometryNodeGroup",
                        "label": "Pick SideAlong DeltaX",
                        "node_tree": pickvectorcomp,
                    },
                    {
                        "type_id": "GeometryNodeGroup",
                        "label": "Pick SideAcross SizeX",
                        "node_tree": pickvectorcomp,
                    },
                    {
                        "type_id": "GeometryNodeGroup",
                        "label": "Pick SideAcross DeltaX",
                        "node_tree": pickvectorcomp,
                    },
                    {
                        "type_id": "ShaderNodeCombineXYZ",
                        "label": "Combine Translations",
                    },
                    {
                        "type_id": "ShaderNodeCombineXYZ",
                        "label": "Combine Rotations",
                    },
                ],
                [
                    {
                        "type_id": "ShaderNodeCombineXYZ",
                        "label": "Combine SideAlong Size",
                    },
                    {
                        "type_id": "GeometryNodeGroup",
                        "label": "Plane1",
                        "node_tree": genticks,
                    },
                    {
                        "type_id": "GeometryNodeGroup",
                        "label": "Transform Plane1",
                        "node_tree": planetransform,
                        "height": 1.5,
                    },
                    {
                        "type_id": "GeometryNodeGroup",
                        "label": "Plane2",
                        "node_tree": genticks,
                    },
                    {
                        "type_id": "GeometryNodeGroup",
                        "label": "Transform Plane2",
                        "node_tree": planetransform,
                        "height": 1.5,
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeTransform",
                        "label": "Transform Plane1 Final",
                    },
                    {
                        "type_id": "GeometryNodeTransform",
                        "label": "Transform Plane2 Preliminary",
                        "input_defaults": {2: (0, 0, 1.5708)},
                        "height": 1.5,
                    },
                    {
                        "type_id": "GeometryNodeTransform",
                        "label": "Transform Plane2 Final",
                        "height": 1.5,
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeJoinGeometry",
                        "label": "Join Geometry",
                    }
                ],
                [
                    {
                        "type_id": "NodeGroupOutput",
                        "label": "Group Output",
                        "is_active_output": True,
                    }
                ],
            ],
            socket_kwargs=[
                {
                    "name": "Sizes",
                    "in_out": "INPUT",
                    "type": "NodeSocketVector",
                },
                {
                    "name": "Deltas",
                    "in_out": "INPUT",
                    "type": "NodeSocketVector",
                },
                {
                    "name": "SideAlong",
                    "in_out": "INPUT",
                    "type": "NodeSocketInt",
                },
                {
                    "name": "SideAcross",
                    "in_out": "INPUT",
                    "type": "NodeSocketInt",
                },
                {
                    "name": "TranslateInX",
                    "in_out": "INPUT",
                    "type": "NodeSocketBool",
                },
                {
                    "name": "TranslateInY",
                    "in_out": "INPUT",
                    "type": "NodeSocketBool",
                },
                {
                    "name": "TranslateInZ",
                    "in_out": "INPUT",
                    "type": "NodeSocketBool",
                },
                {
                    "name": "RotateInX",
                    "in_out": "INPUT",
                    "type": "NodeSocketBool",
                },
                {
                    "name": "RotateInY",
                    "in_out": "INPUT",
                    "type": "NodeSocketBool",
                },
                {
                    "name": "RotateInZ",
                    "in_out": "INPUT",
                    "type": "NodeSocketBool",
                },
                {
                    "name": "Plane",
                    "in_out": "OUTPUT",
                    "type": "NodeSocketGeometry",
                },
            ],
            node_links=[
                (("GroupInput", "Sizes"), ("PickSideAlongSizeX", "Vector")),
                (("GroupInput", "Sizes"), ("PickSideAcrossSizeX", "Vector")),
                (("GroupInput", "Sizes"), ("TransformPlane1", "Sizes")),
                (("GroupInput", "Sizes"), ("TransformPlane2", "Sizes")),
                (("GroupInput", "Deltas"), ("PickSideAlongDeltaX", "Vector")),
                (("GroupInput", "Deltas"), ("PickSideAcrossDeltaX", "Vector")),
                (("GroupInput", "SideAlong"), ("PickSideAlongSizeX", "PickComponent")),
                (("GroupInput", "SideAlong"), ("PickSideAlongDeltaX", "PickComponent")),
                (
                    ("GroupInput", "SideAcross"),
                    ("PickSideAcrossSizeX", "PickComponent"),
                ),
                (
                    ("GroupInput", "SideAcross"),
                    ("PickSideAcrossDeltaX", "PickComponent"),
                ),
                (("GroupInput", "TranslateInX"), ("CombineTranslations", "X")),
                (("GroupInput", "TranslateInY"), ("CombineTranslations", "Y")),
                (("GroupInput", "TranslateInZ"), ("CombineTranslations", "Z")),
                (("GroupInput", "RotateInX"), ("CombineRotations", "X")),
                (("GroupInput", "RotateInY"), ("CombineRotations", "Y")),
                (("GroupInput", "RotateInZ"), ("CombineRotations", "Z")),
                (("PickSideAlongSizeX", "Component"), ("CombineSideAlongSize", "X")),
                (("PickSideAlongSizeX", "Component"), ("Plane1", "Size")),
                (
                    ("PickSideAlongSizeX", "Component"),
                    ("TransformPlane2", "SizeAcross"),
                ),
                (("PickSideAlongDeltaX", "Component"), ("Plane1", "Delta")),
                (
                    ("PickSideAcrossSizeX", "Component"),
                    ("TransformPlane1", "SizeAcross"),
                ),
                (("PickSideAcrossSizeX", "Component"), ("Plane2", "Size")),
                (("PickSideAcrossDeltaX", "Component"), ("Plane2", "Delta")),
                (
                    ("CombineTranslations", "Vector"),
                    ("TransformPlane1", "TranslateInXYZ"),
                ),
                (
                    ("CombineTranslations", "Vector"),
                    ("TransformPlane2", "TranslateInXYZ"),
                ),
                (("CombineRotations", "Vector"), ("TransformPlane1", "RotateInXYZ")),
                (("CombineRotations", "Vector"), ("TransformPlane2", "RotateInXYZ")),
                (
                    ("CombineSideAlongSize", "Vector"),
                    ("TransformPlane2Preliminary", "Translation"),
                ),
                (("Plane1", "Geometry"), ("TransformPlane1Final", "Geometry")),
                (
                    ("TransformPlane1", "Translation"),
                    ("TransformPlane1Final", "Translation"),
                ),
                (("TransformPlane1", "Rotation"), ("TransformPlane1Final", "Rotation")),
                (("TransformPlane1", "Stretch"), ("TransformPlane1Final", "Scale")),
                (("Plane2", "Geometry"), ("TransformPlane2Preliminary", "Geometry")),
                (
                    ("TransformPlane2", "Translation"),
                    ("TransformPlane2Final", "Translation"),
                ),
                (("TransformPlane2", "Rotation"), ("TransformPlane2Final", "Rotation")),
                (
                    ("TransformPlane2", "Stretch"),
                    ("TransformPlane2Preliminary", "Scale"),
                ),
                (("TransformPlane1Final", "Geometry"), ("JoinGeometry", 0)),
                (
                    ("TransformPlane2Preliminary", "Geometry"),
                    ("TransformPlane2Final", "Geometry"),
                ),
                (("TransformPlane2Final", "Geometry"), ("JoinGeometry", 0)),
                (("JoinGeometry", 0), ("GroupOutput", "Plane")),
            ],
            node_tree=plane,
            clear=True,
        )

        return plane

    plane = generate_plane()

    def generate_outliner():
        outliner = bpy.data.node_groups.new(type="GeometryNodeTree", name="Outliner")

        CreateNodes(
            node_kwargs=[
                [
                    {
                        "type_id": "NodeGroupInput",
                        "label": "Group Input",
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeCurvePrimitiveCircle",
                        "label": "Curve Profile",
                    },
                    {
                        "type_id": "GeometryNodeCurveToMesh",
                        "label": "Curve To Mesh",
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeMeshToCurve",
                        "label": "Mesh To Curve",
                    },
                    {
                        "type_id": "GeometryNodeMeshBoolean",
                        "label": "Mesh Boolean",
                        "operation": "UNION",
                        "solver": "FLOAT",
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeCurveToMesh",
                        "label": "Curve To Mesh Final",
                        "input_defaults": {
                            (3 if bpy.app.version >= (4, 5, 0) else 2): True
                        },
                    },
                ],
                [
                    {
                        "type_id": "NodeGroupOutput",
                        "label": "Group Output",
                        "is_active_output": True,
                    }
                ],
            ],
            socket_kwargs=[
                {
                    "name": "Curve",
                    "in_out": "INPUT",
                    "type": "NodeSocketGeometry",
                },
                {
                    "name": "Resolution",
                    "in_out": "INPUT",
                    "type": "NodeSocketInt",
                },
                {
                    "name": "Radius",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Mesh",
                    "in_out": "OUTPUT",
                    "type": "NodeSocketGeometry",
                },
            ],
            node_links=[
                (("GroupInput", "Curve"), ("CurveToMesh", "Curve")),
                (("GroupInput", "Resolution"), ("CurveProfile", "Resolution")),
                (("GroupInput", "Radius"), ("CurveProfile", "Radius")),
                (("CurveProfile", "Curve"), ("CurveToMeshFinal", "Profile Curve")),
                (("CurveToMesh", "Mesh"), ("MeshBoolean", "Mesh")),
                (("MeshBoolean", "Mesh"), ("MeshToCurve", "Mesh")),
                (("MeshToCurve", "Curve"), ("CurveToMeshFinal", "Curve")),
                (("CurveToMeshFinal", "Mesh"), ("GroupOutput", "Mesh")),
            ],
            node_tree=outliner,
            clear=True,
        )

        return outliner

    outliner = generate_outliner()

    axes_grid = bpy.data.node_groups.new(type="GeometryNodeTree", name="AxesGrid")
    all_nodes = CreateNodes(
        node_kwargs=[
            [
                {
                    "type_id": "NodeGroupInput",
                    "label": "Group Input",
                },
            ],
            [
                {
                    "type_id": "GeometryNodeGroup",
                    "label": f"{sign}{XYZ}",
                    "node_tree": plane,
                    "height": 1.5,
                }
                for sign in "+-"
                for XYZ in "XYZ"
            ],
            [
                {
                    "type_id": "GeometryNodeSwitch",
                    "label": f"Switch {sign}{XYZ}",
                }
                for sign in "+-"
                for XYZ in "XYZ"
            ],
            [
                {
                    "type_id": "GeometryNodeJoinGeometry",
                    "label": "Join Geometry",
                },
            ],
            [
                {
                    "type_id": "GeometryNodeGroup",
                    "label": "Outline",
                    "node_tree": outliner,
                },
            ],
            [
                {
                    "type_id": "GeometryNodeSetMaterial",
                    "label": "Set Material",
                    "input_defaults": {"Material": mat},
                },
            ],
            [
                {
                    "type_id": "NodeGroupOutput",
                    "label": "Group Output",
                    "is_active_output": True,
                }
            ],
        ],
        socket_kwargs=[
            {
                "name": "Sizes",
                "in_out": "INPUT",
                "type": "NodeSocketVector",
                "default_value": (10, 10, 10),
            },
            {
                "name": "Deltas",
                "in_out": "INPUT",
                "type": "NodeSocketVector",
                "default_value": (1, 1, 1),
            },
        ]
        + [
            {
                "name": f"{sign}{XYZ}",
                "in_out": "INPUT",
                "type": "NodeSocketBool",
                "default_value": sign == "-",
            }
            for XYZ in "XYZ"
            for sign in "+-"
        ]
        + [
            {
                "name": "Resolution",
                "in_out": "INPUT",
                "type": "NodeSocketInt",
                "default_value": 16,
            },
            {
                "name": "Radius",
                "in_out": "INPUT",
                "type": "NodeSocketFloat",
                "default_value": 0.01,
            },
            {
                "name": "Geometry",
                "in_out": "OUTPUT",
                "type": "NodeSocketGeometry",
            },
        ],
        node_links=[
            (("GroupInput", quantity), (f"{sign}{XYZ}", quantity))
            for quantity in ["Sizes", "Deltas"]
            for XYZ in "XYZ"
            for sign in "+-"
        ]
        + [
            ((f"{sign}{XYZ}", "Plane"), (f"Switch{sign}{XYZ}", "True"))
            for XYZ in "XYZ"
            for sign in "+-"
        ]
        + [
            (("GroupInput", f"{sign}{XYZ}"), (f"Switch{sign}{XYZ}", "Switch"))
            for XYZ in "XYZ"
            for sign in "+-"
        ]
        + [
            ((f"Switch{sign}{XYZ}", "Output"), (f"JoinGeometry", 0))
            for XYZ in "XYZ"
            for sign in "+-"
        ]
        + [
            (("JoinGeometry", 0), ("Outline", "Curve")),
            (("GroupInput", "Resolution"), ("Outline", "Resolution")),
            (("GroupInput", "Radius"), ("Outline", "Radius")),
            (("Outline", "Mesh"), ("SetMaterial", "Geometry")),
            (("SetMaterial", "Geometry"), ("GroupOutput", "Geometry")),
        ],  # pyright: ignore[reportArgumentType]
        node_tree=axes_grid,
        clear=True,
    )

    all_nodes["+X"].inputs["SideAlong"].default_value = 1
    all_nodes["+X"].inputs["SideAcross"].default_value = 2
    all_nodes["+X"].inputs["TranslateInX"].default_value = True
    all_nodes["+X"].inputs["RotateInX"].default_value = True
    all_nodes["+X"].inputs["RotateInZ"].default_value = True

    all_nodes["-X"].inputs["SideAlong"].default_value = 1
    all_nodes["-X"].inputs["SideAcross"].default_value = 2
    all_nodes["-X"].inputs["RotateInX"].default_value = True
    all_nodes["-X"].inputs["RotateInZ"].default_value = True

    all_nodes["+Y"].inputs["SideAlong"].default_value = 0
    all_nodes["+Y"].inputs["SideAcross"].default_value = 2
    all_nodes["+Y"].inputs["TranslateInY"].default_value = True
    all_nodes["+Y"].inputs["RotateInX"].default_value = True

    all_nodes["-Y"].inputs["SideAlong"].default_value = 0
    all_nodes["-Y"].inputs["SideAcross"].default_value = 2
    all_nodes["-Y"].inputs["RotateInX"].default_value = True

    all_nodes["+Z"].inputs["SideAlong"].default_value = 0
    all_nodes["+Z"].inputs["SideAcross"].default_value = 1
    all_nodes["+Z"].inputs["TranslateInZ"].default_value = True

    all_nodes["-Z"].inputs["SideAlong"].default_value = 0
    all_nodes["-Z"].inputs["SideAcross"].default_value = 1

    return axes_grid


def Arrow_geometry_node(mat: bpy.types.Material) -> bpy.types.NodeTree:
    def make_cylindrical_arrow():
        cylindrical_arrow = bpy.data.node_groups.new(
            type="GeometryNodeTree", name="CylindricalArrow"
        )
        CreateNodes(
            node_kwargs=[
                [
                    {
                        "type_id": "NodeGroupInput",
                        "label": "Group Input",
                    }
                ],
                [
                    {
                        "type_id": "ShaderNodeMath",
                        "label": "HalfHeight",
                        "operation": "DIVIDE",
                        "input_defaults": {1: 2},
                    },
                    {
                        "type_id": "ShaderNodeCombineXYZ",
                        "label": "TranslateArrowhead",
                    },
                    {
                        "type_id": "ShaderNodeMath",
                        "label": "HalfWidth",
                        "operation": "DIVIDE",
                        "input_defaults": {1: 2},
                    },
                    {
                        "type_id": "ShaderNodeMath",
                        "label": "HalfHeadWidth",
                        "operation": "DIVIDE",
                        "input_defaults": {1: 2},
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeMeshCylinder",
                        "label": "Cylinder",
                    },
                    {
                        "type_id": "GeometryNodeMeshCone",
                        "label": "Cone",
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeJoinGeometry",
                        "label": "Join Geometry",
                    },
                    {
                        "type_id": "GeometryNodeSetPosition",
                        "label": "Z Offset",
                    },
                ],
                [
                    {
                        "type_id": "NodeGroupOutput",
                        "label": "Group Output",
                        "is_active_output": True,
                    }
                ],
            ],
            socket_kwargs=[
                {
                    "name": "Arrow Height",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Arrow Width",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Arrowhead Height",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Arrowhead Width",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Resolution",
                    "in_out": "INPUT",
                    "type": "NodeSocketInt",
                },
                {
                    "name": "Geometry",
                    "in_out": "OUTPUT",
                    "type": "NodeSocketGeometry",
                },
            ],
            node_links=[
                (("GroupInput", "Arrow Height"), ("Cylinder", "Depth")),
                (("GroupInput", "Arrow Height"), ("HalfHeight", 0)),
                (("GroupInput", "Arrow Width"), ("HalfWidth", 0)),
                (("GroupInput", "Arrowhead Height"), ("Cone", "Depth")),
                (("GroupInput", "Arrowhead Width"), ("HalfHeadWidth", 0)),
                (("GroupInput", "Resolution"), ("Cylinder", "Vertices")),
                (("GroupInput", "Resolution"), ("Cone", "Vertices")),
                (("HalfHeight", "Value"), ("TranslateArrowhead", "Z")),
                (("TranslateArrowhead", "Vector"), ("ZOffset", "Offset")),
                (("HalfWidth", "Value"), ("Cylinder", "Radius")),
                (("HalfHeadWidth", "Value"), ("Cone", "Radius Bottom")),
                (("Cylinder", "Mesh"), ("JoinGeometry", 0)),
                (("Cone", "Mesh"), ("ZOffset", "Geometry")),
                (("ZOffset", "Geometry"), ("JoinGeometry", 0)),
                (("JoinGeometry", 0), ("GroupOutput", "Geometry")),
            ],
            node_tree=cylindrical_arrow,
            clear=True,
        )

        return cylindrical_arrow

    def make_flat_arrow():
        flat_arrow = bpy.data.node_groups.new(type="GeometryNodeTree", name="FlatArrow")
        CreateNodes(
            node_kwargs=[
                [
                    {
                        "type_id": "NodeGroupInput",
                        "label": "Group Input",
                    }
                ],
                [
                    {
                        "type_id": "ShaderNodeCombineXYZ",
                        "label": "Cube Size",
                    },
                    {
                        "type_id": "ShaderNodeMath",
                        "label": "Half Height",
                        "operation": "DIVIDE",
                        "input_defaults": {1: 2},
                    },
                    {
                        "type_id": "ShaderNodeCombineXYZ",
                        "label": "Z Offset",
                    },
                    {
                        "type_id": "ShaderNodeMath",
                        "label": "Half Head Width",
                        "operation": "DIVIDE",
                        "input_defaults": {1: 2},
                    },
                    {
                        "type_id": "ShaderNodeCombineXYZ",
                        "label": "Triangle Size",
                    },
                    {
                        "type_id": "ShaderNodeMath",
                        "label": "Half Thickness",
                        "operation": "DIVIDE",
                        "input_defaults": {1: 2},
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeMeshCube",
                        "label": "Cube",
                    },
                    {
                        "type_id": "GeometryNodePoints",
                        "label": "Point A",
                        "input_defaults": {1: (1, 0, 0)},
                    },
                    {
                        "type_id": "GeometryNodePoints",
                        "label": "Point B",
                        "input_defaults": {1: (-1, 0, 0)},
                    },
                    {
                        "type_id": "GeometryNodePoints",
                        "label": "Point C",
                        "input_defaults": {1: (0, 0, 1)},
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeJoinGeometry",
                        "label": "Join Geometry",
                    },
                    {
                        "type_id": "GeometryNodeExtrudeMesh",
                        "label": "Add Thickness",
                    },
                    {
                        "type_id": "GeometryNodeTransform",
                        "label": "Transform Arrowhead",
                    },
                    {
                        "type_id": "GeometryNodeConvexHull",
                        "label": "Build Triangle",
                    },
                    {
                        "type_id": "GeometryNodeJoinGeometry",
                        "label": "Join Points",
                    },
                ],
                [
                    {
                        "type_id": "NodeGroupOutput",
                        "label": "Group Output",
                        "is_active_output": True,
                    }
                ],
            ],
            socket_kwargs=[
                {
                    "name": "Arrow Height",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Arrow Width",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Arrowhead Height",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Arrowhead Width",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Thickness",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Geometry",
                    "in_out": "OUTPUT",
                    "type": "NodeSocketGeometry",
                },
            ],
            node_links=[
                (("GroupInput", "Arrow Height"), ("CubeSize", "Z")),
                (("GroupInput", "Arrow Height"), ("HalfHeight", 0)),
                (("GroupInput", "Arrow Width"), ("CubeSize", "X")),
                (("GroupInput", "Arrowhead Height"), ("TriangleSize", "Z")),
                (("GroupInput", "Arrowhead Width"), ("HalfHeadWidth", 0)),
                (("GroupInput", "Thickness"), ("CubeSize", "Y")),
                (("GroupInput", "Thickness"), ("HalfThickness", 0)),
                (("CubeSize", "Vector"), ("Cube", "Size")),
                (("HalfHeight", "Value"), ("ZOffset", "Z")),
                (("ZOffset", "Vector"), ("TransformArrowhead", "Translation")),
                (("HalfHeadWidth", "Value"), ("TriangleSize", "X")),
                (("TriangleSize", "Vector"), ("TransformArrowhead", "Scale")),
                (("HalfThickness", "Value"), ("AddThickness", "Offset Scale")),
                (("Cube", "Mesh"), ("JoinGeometry", 0)),
                (("AddThickness", "Mesh"), ("JoinGeometry", 0)),
                (("TransformArrowhead", "Geometry"), ("AddThickness", "Mesh")),
                (("BuildTriangle", "Convex Hull"), ("TransformArrowhead", "Geometry")),
                (("BuildTriangle", "Convex Hull"), ("TransformArrowhead", "Geometry")),
                (("JoinPoints", 0), ("BuildTriangle", "Geometry")),
                (("PointA", "Points"), ("JoinPoints", 0)),
                (("PointB", "Points"), ("JoinPoints", 0)),
                (("PointC", "Points"), ("JoinPoints", 0)),
                (("JoinGeometry", 0), ("GroupOutput", "Geometry")),
            ],
            node_tree=flat_arrow,
            clear=True,
        )
        return flat_arrow

    cylindrical_arrow = make_cylindrical_arrow()
    flat_arrow = make_flat_arrow()

    arrow_obj = bpy.data.node_groups.new(type="GeometryNodeTree", name="Arrow")
    all_nodes = CreateNodes(
        node_kwargs=[
            [
                {
                    "type_id": "NodeGroupInput",
                    "label": "Group Input",
                },
            ],
            [
                {
                    "type_id": "GeometryNodeGroup",
                    "label": "Cylindrical",
                    "node_tree": cylindrical_arrow,
                },
                {
                    "type_id": "GeometryNodeGroup",
                    "label": "Flat",
                    "node_tree": flat_arrow,
                },
            ],
            [
                {
                    "type_id": "GeometryNodeSwitch",
                    "label": "Switch",
                    "input_type": "GEOMETRY",
                },
            ],
            [
                {
                    "type_id": "GeometryNodeSetShadeSmooth",
                    "label": "Smooth Shade",
                },
            ],
            [
                {
                    "type_id": "GeometryNodeSetMaterial",
                    "label": "Set Material",
                    "input_defaults": {"Material": mat},
                },
            ],
            [
                {
                    "type_id": "NodeGroupOutput",
                    "label": "Group Output",
                    "is_active_output": True,
                }
            ],
        ],
        socket_kwargs=[
            {
                "name": "Cylindrical Arrow",
                "in_out": "INPUT",
                "type": "NodeSocketBool",
                "default_value": False,
            },
            {
                "name": "Arrow Height",
                "in_out": "INPUT",
                "type": "NodeSocketFloat",
                "default_value": 2.0,
            },
            {
                "name": "Arrow Width",
                "in_out": "INPUT",
                "type": "NodeSocketFloat",
                "default_value": 0.5,
            },
            {
                "name": "Arrowhead Height",
                "in_out": "INPUT",
                "type": "NodeSocketFloat",
                "default_value": 1.0,
            },
            {
                "name": "Arrowhead Width",
                "in_out": "INPUT",
                "type": "NodeSocketFloat",
                "default_value": 1.0,
            },
            {
                "name": "Resolution",
                "in_out": "INPUT",
                "type": "NodeSocketInt",
                "default_value": 32,
            },
            {
                "name": "Thickness",
                "in_out": "INPUT",
                "type": "NodeSocketFloat",
                "default_value": 0.1,
            },
            {
                "name": "Geometry",
                "in_out": "OUTPUT",
                "type": "NodeSocketGeometry",
            },
        ],
        node_links=[
            (("GroupInput", "Cylindrical Arrow"), ("Switch", "Switch")),
            (("GroupInput", "Arrow Height"), ("Cylindrical", "Arrow Height")),
            (("GroupInput", "Arrow Height"), ("Flat", "Arrow Height")),
            (("GroupInput", "Arrow Width"), ("Cylindrical", "Arrow Width")),
            (("GroupInput", "Arrow Width"), ("Flat", "Arrow Width")),
            (("GroupInput", "Arrowhead Height"), ("Cylindrical", "Arrowhead Height")),
            (("GroupInput", "Arrowhead Height"), ("Flat", "Arrowhead Height")),
            (("GroupInput", "Arrowhead Width"), ("Cylindrical", "Arrowhead Width")),
            (("GroupInput", "Arrowhead Width"), ("Flat", "Arrowhead Width")),
            (("GroupInput", "Resolution"), ("Cylindrical", "Resolution")),
            (("GroupInput", "Thickness"), ("Flat", "Thickness")),
            (("Cylindrical", "Geometry"), ("Switch", "True")),
            (("Flat", "Geometry"), ("Switch", "False")),
            (("Switch", "Output"), ("SmoothShade", "Geometry")),
            (("SmoothShade", "Geometry"), ("SetMaterial", "Geometry")),
            (("SetMaterial", "Geometry"), ("GroupOutput", "Geometry")),
        ],
        node_tree=arrow_obj,
        clear=True,
    )

    return arrow_obj


def Origin_axes_node(mat: bpy.types.Material | None = None) -> bpy.types.NodeTree:
    def generate_axis_arrow():
        axis = bpy.data.node_groups.new(type="GeometryNodeTree", name="Axis")

        CreateNodes(
            node_kwargs=[
                [
                    {
                        "type_id": "NodeGroupInput",
                        "label": "Group Input",
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeMeshCylinder",
                        "label": "Cylinder",
                    },
                    {
                        "type_id": "GeometryNodeSetPosition",
                        "label": "CylinderPosition",
                    },
                    {
                        "type_id": "ShaderNodeCombineXYZ",
                        "label": "Cylinder Z Offset",
                    },
                    {
                        "type_id": "ShaderNodeMath",
                        "label": "Half Height",
                        "operation": "DIVIDE",
                        "input_defaults": {1: 2},
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeMeshCone",
                        "label": "Cone",
                    },
                    {
                        "type_id": "GeometryNodeSetPosition",
                        "label": "Cone Position",
                    },
                    {
                        "type_id": "ShaderNodeCombineXYZ",
                        "label": "Cone Z Offset",
                    },
                    {
                        "type_id": "ShaderNodeMath",
                        "label": "Arrow Height",
                        "operation": "DIVIDE",
                        "input_defaults": {1: 3},
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeJoinGeometry",
                        "label": "Join Geometry",
                    },
                ],
                [
                    {
                        "type_id": "GeometryNodeTransform",
                        "label": "Transform Geometry",
                    },
                ],
                [
                    {
                        "type_id": "NodeGroupOutput",
                        "label": "Group Output",
                        "is_active_output": True,
                    }
                ],
            ],
            socket_kwargs=[
                {
                    "name": "Length",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Radius",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Arrowsize",
                    "in_out": "INPUT",
                    "type": "NodeSocketFloat",
                },
                {
                    "name": "Rotation",
                    "in_out": "INPUT",
                    "type": "NodeSocketRotation",
                },
                {
                    "name": "Resolution",
                    "in_out": "INPUT",
                    "type": "NodeSocketInt",
                },
                {
                    "name": "Geometry",
                    "in_out": "OUTPUT",
                    "type": "NodeSocketGeometry",
                },
            ],
            node_links=[
                (("GroupInput", "Length"), ("Cylinder", "Depth")),
                (("GroupInput", "Length"), ("ConeZOffset", "Z")),
                (("GroupInput", "Length"), ("HalfHeight", 0)),
                (("GroupInput", "Radius"), ("Cylinder", "Radius")),
                (("GroupInput", "Arrowsize"), ("Cone", "Depth")),
                (("GroupInput", "Arrowsize"), ("ArrowHeight", 0)),
                (("GroupInput", "Rotation"), ("TransformGeometry", "Rotation")),
                (("GroupInput", "Resolution"), ("Cylinder", "Vertices")),
                (("GroupInput", "Resolution"), ("Cone", "Vertices")),
                (("Cylinder", "Mesh"), ("CylinderPosition", "Geometry")),
                (("CylinderPosition", "Geometry"), ("JoinGeometry", 0)),
                (("CylinderZOffset", "Vector"), ("CylinderPosition", "Offset")),
                (("HalfHeight", "Value"), ("CylinderZOffset", "Z")),
                (("Cone", "Mesh"), ("ConePosition", "Geometry")),
                (("ConePosition", "Geometry"), ("JoinGeometry", 0)),
                (("ConeZOffset", "Vector"), ("ConePosition", "Offset")),
                (("ArrowHeight", "Value"), ("Cone", "Radius Bottom")),
                (("JoinGeometry", 0), ("TransformGeometry", "Geometry")),
                (("TransformGeometry", "Geometry"), ("GroupOutput", "Geometry")),
            ],
            node_tree=axis,
            clear=True,
        )
        return axis

    axis = generate_axis_arrow()

    axes = bpy.data.node_groups.new(type="GeometryNodeTree", name="OriginAxes")
    all_nodes = CreateNodes(
        node_kwargs=[
            [
                {
                    "type_id": "NodeGroupInput",
                    "label": "Group Input",
                },
            ],
            [
                {
                    "type_id": "GeometryNodeGroup",
                    "label": f"{XYZ} Axis",
                    "node_tree": axis,
                }
                for XYZ in "XYZ"
            ]
            + [
                {"type_id": "GeometryNodeMeshUVSphere", "label": "Origin"},
                {
                    "type_id": "FunctionNodeIntegerMath",
                    "label": "Half Resolution",
                    "operation": "DIVIDE",
                    "input_defaults": {1: 2},
                },
            ],
            [
                {
                    "type_id": "GeometryNodeStoreNamedAttribute",
                    "label": f"Store {XYZ} Color",
                    "data_type": "FLOAT_COLOR",
                    "domain": "FACE",
                    "input_defaults": {2: "shading"},
                }
                for XYZ in ["X", "Y", "Z", "Origin"]
            ],
            [
                {
                    "type_id": "GeometryNodeJoinGeometry",
                    "label": "Join Geometry",
                },
            ],
            [
                {
                    "type_id": "GeometryNodeSetShadeSmooth",
                    "label": "Smooth Shade",
                },
            ],
            [
                {
                    "type_id": "GeometryNodeSetMaterial",
                    "label": "Set Material",
                    "input_defaults": {"Material": mat},
                },
            ],
            [
                {
                    "type_id": "NodeGroupOutput",
                    "label": "Group Output",
                    "is_active_output": True,
                }
            ],
        ],
        socket_kwargs=[
            {
                "name": "Lengths",
                "in_out": "INPUT",
                "type": "NodeSocketFloat",
                "default_value": 2.0,
            },
            {
                "name": "Thicknesses",
                "in_out": "INPUT",
                "type": "NodeSocketFloat",
                "default_value": 0.1,
            },
            {
                "name": "Arrowsizes",
                "in_out": "INPUT",
                "type": "NodeSocketFloat",
                "default_value": 0.75,
            },
            {
                "name": "Origin Radius",
                "in_out": "INPUT",
                "type": "NodeSocketFloat",
                "default_value": 0.25,
            },
            {
                "name": "X Color",
                "in_out": "INPUT",
                "type": "NodeSocketColor",
                "default_value": (
                    0.9647058823529412,
                    0.21176470588235294,
                    0.3215686274509804,
                    1.0,
                ),
            },
            {
                "name": "Y Color",
                "in_out": "INPUT",
                "type": "NodeSocketColor",
                "default_value": (
                    0.49411764705882355,
                    0.7607843137254902,
                    0.07058823529411765,
                    1.0,
                ),
            },
            {
                "name": "Z Color",
                "in_out": "INPUT",
                "type": "NodeSocketColor",
                "default_value": (
                    0.1843137254901961,
                    0.5176470588235295,
                    0.8941176470588236,
                    1.0,
                ),
            },
            {
                "name": "Origin Color",
                "in_out": "INPUT",
                "type": "NodeSocketColor",
                "default_value": (
                    0.19607843137254902,
                    0.19607843137254902,
                    0.19607843137254902,
                    1.0,
                ),
            },
            {
                "name": "Resolution",
                "in_out": "INPUT",
                "type": "NodeSocketInt",
                "default_value": 32,
            },
            {
                "name": "Geometry",
                "in_out": "OUTPUT",
                "type": "NodeSocketGeometry",
            },
        ],
        node_links=[
            (("GroupInput", q_left), (f"{XYZ}Axis", q_right))
            for XYZ in "XYZ"
            for q_left, q_right in zip(
                ["Lengths", "Thicknesses", "Arrowsizes", "Resolution"],
                ["Length", "Radius", "Arrowsize", "Resolution"],
            )
        ]
        + [
            (("GroupInput", f"{attr} Color"), (f"Store{attr}Color", "Value"))
            for attr in ["X", "Y", "Z", "Origin"]
        ]
        + [
            (("GroupInput", "Origin Radius"), ("Origin", "Radius")),
            (("GroupInput", "Resolution"), ("Origin", "Segments")),
            (("GroupInput", "Resolution"), ("HalfResolution", 0)),
            (("HalfResolution", 0), ("Origin", "Rings")),
        ]
        + [
            ((f"{XYZ}Axis", "Geometry"), (f"Store{XYZ}Color", "Geometry"))
            for XYZ in "XYZ"
        ]
        + [((f"Store{XYZ}Color", "Geometry"), ("JoinGeometry", 0)) for XYZ in "XYZ"]
        + [
            (("Origin", "Mesh"), ("StoreOriginColor", "Geometry")),
            (("StoreOriginColor", "Geometry"), ("JoinGeometry", 0)),
            (("JoinGeometry", 0), ("SmoothShade", "Geometry")),
            (("SmoothShade", "Geometry"), ("SetMaterial", "Geometry")),
            (("SetMaterial", "Geometry"), ("GroupOutput", "Geometry")),
        ],  # pyright: ignore[reportArgumentType]
        node_tree=axes,
        clear=True,
    )
    all_nodes["XAxis"].inputs["Rotation"].default_value = (0, 1.5708, 0)
    all_nodes["YAxis"].inputs["Rotation"].default_value = (1.5708, 0, 3.1416)

    return axes
