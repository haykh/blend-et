import bpy

from ..utilities.nodes import CreateNodes  # pyright: ignore[reportMissingImports]
from ..utilities.materials import (  # pyright: ignore[reportMissingImports]
    CommonMaterialColormapChange,
)


def Create_pointcloud_mesh(
    context: bpy.types.Context,
    raw_object: bpy.types.Object | None = None,
    material: bpy.types.Material | None = None,
    uuid_str: str = "",
):
    suffix = f"_{uuid_str}" if uuid_str != "" else ""

    bpy.ops.object.volume_add(align="WORLD")
    obj = context.active_object
    if obj is None:
        raise RuntimeError("Failed to create empty object")
    obj.name = f"PointcloudGeometry{suffix}"

    nt = bpy.data.node_groups.new(
        type="GeometryNodeTree", name=f"PointcloudGeometryNodes{suffix}"
    )
    obj.modifiers.new(name="GeometryNodes", type="NODES")
    obj.modifiers["GeometryNodes"].node_group = nt

    CreateNodes(
        node_kwargs=[
            [
                {
                    "type_id": "GeometryNodeObjectInfo",
                    "label": "Pointcloud Data",
                    "input_defaults": {0: raw_object},
                },
            ],
            [
                {
                    "type_id": "GeometryNodeInputIndex",
                    "label": "Index",
                    "height": 0.5,
                }
            ]
            + [
                {
                    "type_id": "GeometryNodeInputNamedAttribute",
                    "label": f"Attr {attr.upper()}",
                    "data_type": "FLOAT",
                    "input_defaults": {0: attr},
                }
                for attr in "xyz"
            ],
            [
                {
                    "type_id": "GeometryNodeSampleIndex",
                    "label": f"Sample {attr.upper()}",
                    "data_type": "FLOAT",
                    "domain": "POINT",
                }
                for attr in "xyz"
            ],
            [
                {
                    "type_id": "GeometryNodeAttributeDomainSize",
                    "label": "Number Of Points",
                    "component": "MESH",
                },
                {
                    "type_id": "ShaderNodeCombineXYZ",
                    "label": "Combine XYZ",
                },
            ],
            [
                {
                    "type_id": "GeometryNodePoints",
                    "label": "Points",
                },
                {
                    "type_id": "ShaderNodeMath",
                    "label": "Point Density",
                    "operation": "DIVIDE",
                    "input_defaults": {0: 1000},
                },
                {
                    "type_id": "NodeGroupInput",
                    "label": "Group Input",
                },
            ],
            [
                {
                    "type_id": "GeometryNodePointsToVolume",
                    "label": "Points To Volume",
                    "resolution_mode": "VOXEL_AMOUNT",
                }
            ],
            [
                {
                    "type_id": "GeometryNodeSetMaterial",
                    "label": "Material",
                    "input_defaults": {"Material": material},
                }
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
                "name": "Voxel Resolution",
                "in_out": "INPUT",
                "type": "NodeSocketFloat",
                "description": "Resolution of the volume in voxels",
            },
            {
                "name": "Voxel Size",
                "in_out": "INPUT",
                "type": "NodeSocketFloat",
                "min_value": 0.0,
                "max_value": 3.4028234663852886e38,
                "subtype": "DISTANCE",
                "description": "Voxel sizes",
            },
        ],
        node_links=[
            (("PointcloudData", "Geometry"), ("SampleX", "Geometry")),
            (("PointcloudData", "Geometry"), ("SampleY", "Geometry")),
            (("PointcloudData", "Geometry"), ("SampleZ", "Geometry")),
            (("PointcloudData", "Geometry"), ("NumberOfPoints", "Geometry")),
            (("Index", "Index"), ("SampleX", "Index")),
            (("Index", "Index"), ("SampleY", "Index")),
            (("Index", "Index"), ("SampleZ", "Index")),
            (("AttrX", "Attribute"), ("SampleX", "Value")),
            (("AttrY", "Attribute"), ("SampleY", "Value")),
            (("AttrZ", "Attribute"), ("SampleZ", "Value")),
            (("SampleX", "Value"), ("CombineXYZ", "X")),
            (("SampleY", "Value"), ("CombineXYZ", "Y")),
            (("SampleZ", "Value"), ("CombineXYZ", "Z")),
            (("NumberOfPoints", "Point Count"), ("Points", "Count")),
            (("CombineXYZ", "Vector"), ("Points", "Position")),
            (("Points", "Points"), ("PointsToVolume", "Points")),
            (("GroupInput", "Voxel Resolution"), ("PointsToVolume", "Voxel Amount")),
            (("GroupInput", "Voxel Resolution"), ("PointDensity", 1)),
            (("GroupInput", "Voxel Size"), ("PointsToVolume", "Radius")),
            (("PointDensity", "Value"), ("PointsToVolume", "Density")),
            (("PointsToVolume", "Volume"), ("Material", "Geometry")),
            (("Material", "Geometry"), ("GroupOutput", "Geometry")),
        ],
        node_tree=nt,
        clear=True,
    )

    obj.modifiers["GeometryNodes"]["Socket_1"] = 500
    obj.modifiers["GeometryNodes"]["Socket_2"] = 0.02

    return obj


def Create_or_reset_pointcloud_material(name: str):
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
                    "type_id": "ShaderNodeVolumeInfo",
                    "label": "Volume Info",
                }
            ],
            [
                {
                    "type_id": "ShaderNodeMapRange",
                    "label": "Density Map",
                    "height": 1.5,
                },
                {
                    "type_id": "ShaderNodeMapRange",
                    "label": "Emissivity Map",
                    "height": 1.5,
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
                    "type_id": "ShaderNodeVolumePrincipled",
                    "label": "Principled Volume",
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
        node_links=[],
        node_tree=mat.node_tree,
        clear=False,
    )

    return mat


def On_material_colormap_change(self, _: bpy.types.Context):
    """Update callback: self is the Material that owns 'pointcloud_colormap'."""
    if not getattr(self, "use_nodes", False) or not self.node_tree:
        return None
    CommonMaterialColormapChange(
        cmap_attr=getattr(self, "pointcloud_colormap", 0),
        cmap_reversed_attr=bool(getattr(self, "pointcloud_colormap_reversed", False)),
        name=self.name,
        create_or_reset_callback=Create_or_reset_pointcloud_material,
        nt=self.node_tree,
    )
