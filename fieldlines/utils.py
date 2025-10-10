import bpy, bmesh
import numpy as np

from ..colormaps.data import (  # pyright: ignore[reportMissingImports]
    Resolve_cmap_id,
    Stops_for_colormap,
    Apply_stops_to_colorramp,
)

from ..utilities.nodes import CreateNodes  # pyright: ignore[reportMissingImports]


def Create_raw_data_fieldline(
    data: dict[str, list[float] | np.ndarray],
    context: bpy.types.Context,
    collection: bpy.types.Collection | None = None,
    i: int = 0,
) -> tuple[bpy.types.Object, bpy.types.Collection]:
    """Encodes a dictionary of arrays as a mesh with point attributes."""
    if (scene := context.scene) is None:
        raise RuntimeError("No active scene found")

    npoints = len(data[list(data.keys())[0]])
    assert all(
        len(v) == npoints for v in data.values()
    ), "Not all arrays have equal lengths"

    if collection is None:
        collection_ = bpy.data.collections.new("FieldlinesRaw")
        scene.collection.children.link(collection_)
        collection_.hide_viewport = True
        collection_.hide_render = True
    else:
        collection_ = collection

    mesh = bpy.data.meshes.new(f"FieldlineRawMesh_{i}")
    obj = bpy.data.objects.new(f"FieldlineRawObj_{i}", mesh)
    collection_.objects.link(obj)

    bm = bmesh.new()

    for i in range(npoints):
        bm.verts.new((i * 0.1, 0.0, 0.0))
    bm.verts.ensure_lookup_table()

    bm.to_mesh(mesh)
    bm.free()

    for k, v in data.items():
        attr_k = mesh.attributes.new(name=k, type="FLOAT", domain="POINT")
        for i in range(npoints):
            attr_k.data[i].value = float(v[i])

    mesh.update()

    return obj, collection_


def Create_fieldline_geometry(
    context: bpy.types.Context,
    raw_collection: bpy.types.Collection | None = None,
    uuid_str: str = "",
):
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
                    "label": f"Attr {xyz.upper()}",
                    "data_type": "FLOAT",
                    "input_defaults": {0: xyz},
                }
                for xyz in "xyz"
            ],
            [
                {
                    "type_id": "GeometryNodeSampleIndex",
                    "label": f"Sample {xyz.upper()}",
                    "domain": "POINT",
                    "data_type": "FLOAT",
                }
                for xyz in "xyz"
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
                }
            ],
            [
                {
                    "type_id": "GeometryNodePointsToCurves",
                    "label": "Points To Curves",
                },
                {
                    "type_id": "NodeGroupInput",
                    "label": "Group Input",
                },
            ],
            [
                {
                    "type_id": "GeometryNodeCurveToMesh",
                    "label": "Curves To Mesh",
                    "input_defaults": {"Fill Caps": True, "Scale": 1.0},
                },
                {
                    "type_id": "GeometryNodeCurvePrimitiveCircle",
                    "label": "Circle Profile",
                    "mode": "RADIUS",
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
        ],
        node_links=[
            (("RawFieldlines", "Instances"), ("CaptureFieldlineIndex", "Geometry")),
            (("FieldlineIndex", "Index"), ("CaptureFieldlineIndex", "Index")),
            (("CaptureFieldlineIndex", "Geometry"), ("RealizeFieldlines", "Geometry")),
            (("RealizeFieldlines", "Geometry"), ("PointPositions", "Geometry")),
            (("RealizeFieldlines", "Geometry"), ("SampleX", "Geometry")),
            (("RealizeFieldlines", "Geometry"), ("SampleY", "Geometry")),
            (("RealizeFieldlines", "Geometry"), ("SampleZ", "Geometry")),
            (("AttrX", "Attribute"), ("SampleX", "Value")),
            (("AttrY", "Attribute"), ("SampleY", "Value")),
            (("AttrZ", "Attribute"), ("SampleZ", "Value")),
            (("PointIndex", "Index"), ("SampleX", "Index")),
            (("PointIndex", "Index"), ("SampleY", "Index")),
            (("PointIndex", "Index"), ("SampleZ", "Index")),
            (("SampleX", "Value"), ("CombineXYZ", "X")),
            (("SampleY", "Value"), ("CombineXYZ", "Y")),
            (("SampleZ", "Value"), ("CombineXYZ", "Z")),
            (("CombineXYZ", "Vector"), ("PointPositions", "Position")),
            (("PointPositions", "Geometry"), ("ConvertToPoints", "Mesh")),
            (("ConvertToPoints", "Points"), ("PointsToCurves", "Points")),
            (("CaptureFieldlineIndex", "Index"), ("PointsToCurves", "Curve Group ID")),
            (("PointsToCurves", "Curves"), ("CurvesToMesh", "Curve")),
            (("GroupInput", "Resolution"), ("CircleProfile", "Resolution")),
            (("GroupInput", "Radius"), ("CircleProfile", "Radius")),
            (("CircleProfile", "Curve"), ("CurvesToMesh", "Profile Curve")),
            (("CurvesToMesh", "Mesh"), ("GroupOutput", "Geometry")),
        ],
        node_tree=nt,
        clear=True,
    )
    obj.modifiers["GeometryNodes"]["Socket_1"] = 8
    obj.modifiers["GeometryNodes"]["Socket_2"] = 0.5


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

    if (nt := mat.node_tree) is None:
        raise RuntimeError("Failed to access node tree of material")
    nodes = nt.nodes
    links = nt.links

    def _get_or_new(nodes, type_id, name=None, label=None, location=None):
        n = nodes.get(name) if name else None
        if n is None:
            n = nodes.new(type_id)
            if name:
                n.name = name
            if label:
                n.label = label
            if location:
                n.location = location
        return n

    # Attribute node
    attr_node = _get_or_new(
        nodes,
        "ShaderNodeAttribute",
        "AttrNode",
        "Attribute Node",
        (-300, 0),
    )
    attr_node.attribute_name = "color"

    color_ramp = _get_or_new(
        nodes,
        "ShaderNodeValToRGB",
        "Colormap",
        "Colormap",
        (0, 0),
    )
    principled_bsdf = _get_or_new(
        nodes,
        "ShaderNodeBsdfPrincipled",
        "PrincipledBSDF",
        "Principled BSDF",
        (300, 0),
    )
    material_output = _get_or_new(
        nodes,
        "ShaderNodeOutputMaterial",
        "MaterialOutput",
        "Material Output",
        (600, 0),
    )

    def _link_if_missing(a, b):
        if not b.links or all(l.from_socket is not a for l in b.links):
            links.new(a, b)

    _link_if_missing(attr_node.outputs["Fac"], color_ramp.inputs["Fac"])
    _link_if_missing(color_ramp.outputs["Color"], principled_bsdf.inputs["Base Color"])
    _link_if_missing(
        color_ramp.outputs["Color"], principled_bsdf.inputs["Emission Color"]
    )
    principled_bsdf.inputs["Emission Strength"].default_value = 0.25
    _link_if_missing(principled_bsdf.outputs["BSDF"], material_output.inputs["Surface"])

    cm_id = Resolve_cmap_id(getattr(mat, "fieldline_colormap", 0))
    rev = bool(getattr(mat, "fieldline_colormap_reversed", False))
    Apply_stops_to_colorramp(
        color_ramp.color_ramp, Stops_for_colormap(cm_id, reverse=rev)
    )

    return mat


def On_material_colormap_change(self, context):
    """Update callback: self is the Material that owns 'fieldline_colormap'."""
    if not getattr(self, "use_nodes", False) or not self.node_tree:
        return None
    nt = self.node_tree
    ramp_node = nt.nodes.get("Colormap")
    if ramp_node is None or ramp_node.type != "VALTORGB":
        Create_or_reset_fieldline_material(self.name)
        ramp_node = nt.nodes.get("Colormap")
    if ramp_node:
        cm_id = Resolve_cmap_id(getattr(self, "fieldline_colormap", 0))
        rev = bool(getattr(self, "fieldline_colormap_reversed", False))
        stops = Stops_for_colormap(cm_id, reverse=rev)
        Apply_stops_to_colorramp(ramp_node.color_ramp, stops)
    return None
