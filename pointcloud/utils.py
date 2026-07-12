import bpy

from ..colormaps.data import (
    Resolve_cmap_id,
    Stops_for_colormap,
    Apply_stops_to_colorramp,
)

from ..utilities.nodes import CreateNodes
from ..utilities.materials import (
    CommonMaterialColormapChange,
)


def Create_pointcloud_mesh(
    context: bpy.types.Context,
    raw_object: bpy.types.Object | None = None,
    material_volume: bpy.types.Material | None = None,
    material_mesh: bpy.types.Material | None = None,
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
                    "type_id": "NodeGroupInput",
                    "label": "Group Input",
                },
                {
                    "type_id": "GeometryNodeInputIndex",
                    "label": "Index",
                    "height": 0.5,
                },
                {
                    "type_id": "GeometryNodeObjectInfo",
                    "label": "Pointcloud Data",
                    "input_defaults": {0: raw_object},
                    "height": 1.5,
                },
            ]
            + [
                {
                    "type_id": "GeometryNodeInputNamedAttribute",
                    "label": f"Attr {attr.upper()}",
                    "data_type": "FLOAT",
                    "input_defaults": {0: attr},
                    "height": 0.75,
                }
                for attr in "xyz"
            ],
            [
                {
                    "type_id": "ShaderNodeMath",
                    "label": "Point Density",
                    "operation": "DIVIDE",
                    "input_defaults": {0: 1000},
                },
                {
                    "type_id": "GeometryNodeAttributeDomainSize",
                    "label": "Number Of Points",
                    "component": "MESH",
                },
                {
                    "type_id": "FunctionNodeIntegerMath",
                    "label": "N/Stride",
                    "operation": "DIVIDE",
                },
            ],
            [
                {
                    "type_id": "GeometryNodeSwitch",
                    "label": "Switch Count",
                    "input_type": "INT",
                },
                {
                    "type_id": "GeometryNodeSwitch",
                    "label": "Switch Index",
                    "input_type": "INT",
                },
                {
                    "type_id": "FunctionNodeIntegerMath",
                    "label": "mod(Index*Stride,N)",
                    "operation": "MODULO",
                },
                {
                    "type_id": "FunctionNodeIntegerMath",
                    "label": "Index*Stride",
                    "operation": "MULTIPLY",
                },
            ],
            [
                {
                    "type_id": "GeometryNodeSampleIndex",
                    "label": f"Sample {attr.upper()}",
                    "data_type": "FLOAT",
                    "domain": "POINT",
                    "height": 1.5,
                }
                for attr in "xyz"
            ],
            [
                {
                    "type_id": "ShaderNodeCombineXYZ",
                    "label": "Combine XYZ",
                },
                {
                    "type_id": "GeometryNodeMeshIcoSphere",
                    "label": "Sphere",
                },
            ],
            [
                {
                    "type_id": "GeometryNodePoints",
                    "label": "Points",
                },
                {
                    "type_id": "GeometryNodeInstanceOnPoints",
                    "label": "Instance Spheres",
                },
            ],
            [
                {
                    "type_id": "GeometryNodePointsToVolume",
                    "label": "Points To Volume",
                    "input_defaults": {"Resolution Mode": "Amount"},
                },
                {
                    "type_id": "GeometryNodeSetShadeSmooth",
                    "label": "Shade Smooth",
                },
            ],
            [
                {
                    "type_id": "GeometryNodeSetMaterial",
                    "label": "Material Volume",
                    "input_defaults": {"Material": material_volume},
                },
                {
                    "type_id": "GeometryNodeSetMaterial",
                    "label": "Material Spheres",
                    "input_defaults": {"Material": material_mesh},
                },
            ],
            [
                {
                    "type_id": "GeometryNodeSwitch",
                    "label": "Switch Geometry",
                    "input_type": "GEOMETRY",
                },
            ],
            [
                {
                    "type_id": "NodeGroupOutput",
                    "label": "Group Output",
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
            {
                "name": "Use Mesh",
                "in_out": "INPUT",
                "type": "NodeSocketBool",
                "description": "Whether to use solid meshes or voxels for pointcloud rendering",
                "default_value": False,
            },
            {
                "name": "Downsampling",
                "in_out": "INPUT",
                "type": "NodeSocketInt",
                "description": "Downsampling factor for pointcloud rendering",
                "default_value": 10,
                "min_value": 1,
            },
            {
                "name": "Sphere Sizes",
                "in_out": "INPUT",
                "type": "NodeSocketFloat",
                "min_value": 0.0,
                "default_value": 0.01,
                "max_value": 3.4028234663852886e38,
                "subtype": "DISTANCE",
                "description": "Sphere sizes",
            },
            {
                "name": "Sphere Resolutions",
                "in_out": "INPUT",
                "type": "NodeSocketInt",
                "default_value": 2,
                "description": "Sphere resolutions",
            },
        ],
        node_links=[
            (("GroupInput", "Voxel Resolution"), ("PointsToVolume", "Voxel Amount")),
            (("GroupInput", "Voxel Resolution"), ("PointDensity", 1)),
            (("GroupInput", "Voxel Size"), ("PointsToVolume", "Radius")),
            (("GroupInput", "Use Mesh"), ("SwitchCount", "Switch")),
            (("GroupInput", "Use Mesh"), ("SwitchIndex", "Switch")),
            (("GroupInput", "Use Mesh"), ("SwitchGeometry", "Switch")),
            (("GroupInput", "Downsampling"), ("N/Stride", 1)),
            (("GroupInput", "Downsampling"), ("Index*Stride", 1)),
            (("GroupInput", "Sphere Sizes"), ("Sphere", "Radius")),
            (("GroupInput", "Sphere Resolutions"), ("Sphere", "Subdivisions")),
            (("Index", "Index"), ("SwitchIndex", "False")),
            (("Index", "Index"), ("Index*Stride", 0)),
            (("PointcloudData", "Geometry"), ("SampleX", "Geometry")),
            (("PointcloudData", "Geometry"), ("SampleY", "Geometry")),
            (("PointcloudData", "Geometry"), ("SampleZ", "Geometry")),
            (("PointcloudData", "Geometry"), ("NumberOfPoints", "Geometry")),
            (("AttrX", "Attribute"), ("SampleX", "Value")),
            (("AttrY", "Attribute"), ("SampleY", "Value")),
            (("AttrZ", "Attribute"), ("SampleZ", "Value")),
            (("PointDensity", "Value"), ("PointsToVolume", "Density")),
            (("NumberOfPoints", "Point Count"), ("N/Stride", 0)),
            (("NumberOfPoints", "Point Count"), ("SwitchCount", "False")),
            (("NumberOfPoints", "Point Count"), ("mod(Index*Stride,N)", 1)),
            (("N/Stride", "Value"), ("SwitchCount", "True")),
            (("SwitchCount", "Output"), ("Points", "Count")),
            (("SwitchIndex", "Output"), ("SampleX", "Index")),
            (("SwitchIndex", "Output"), ("SampleY", "Index")),
            (("SwitchIndex", "Output"), ("SampleZ", "Index")),
            (("mod(Index*Stride,N)", "Value"), ("SwitchIndex", "True")),
            (("Index*Stride", "Value"), ("mod(Index*Stride,N)", 0)),
            (("SampleX", "Value"), ("CombineXYZ", "X")),
            (("SampleY", "Value"), ("CombineXYZ", "Y")),
            (("SampleZ", "Value"), ("CombineXYZ", "Z")),
            (("CombineXYZ", "Vector"), ("Points", "Position")),
            (("Sphere", "Mesh"), ("InstanceSpheres", "Instance")),
            (("Points", "Points"), ("PointsToVolume", "Points")),
            (("Points", "Points"), ("InstanceSpheres", "Points")),
            (("PointsToVolume", "Volume"), ("MaterialVolume", "Geometry")),
            (("InstanceSpheres", "Instances"), ("ShadeSmooth", "Geometry")),
            (("ShadeSmooth", "Geometry"), ("MaterialSpheres", "Geometry")),
            (("MaterialVolume", "Geometry"), ("SwitchGeometry", "False")),
            (("MaterialSpheres", "Geometry"), ("SwitchGeometry", "True")),
            (("SwitchGeometry", "Output"), ("GroupOutput", "Geometry")),
        ],
        node_tree=nt,
        clear=True,
    )

    obj.modifiers["GeometryNodes"]["Socket_1"] = 500
    obj.modifiers["GeometryNodes"]["Socket_2"] = 0.02
    obj.modifiers["GeometryNodes"]["Socket_3"] = False
    obj.modifiers["GeometryNodes"]["Socket_4"] = 100
    obj.modifiers["GeometryNodes"]["Socket_5"] = 1e-2
    obj.modifiers["GeometryNodes"]["Socket_6"] = 2

    return obj


def Create_or_reset_pointcloud_volume_material(name: str):
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

    mat["category"] = "pointcloud_volume"

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
                }
            ],
        ],
        socket_kwargs=[],
        node_links=[
            (("VolumeInfo", "Density"), ("DensityMap", "Value")),
            (("VolumeInfo", "Density"), ("EmissivityMap", "Value")),
            (("DensityMap", "Result"), ("Colormap", "Fac")),
            (("EmissivityMap", "Result"), ("PrincipledVolume", "Emission Strength")),
            (("Colormap", "Color"), ("PrincipledVolume", "Color")),
            (("Colormap", "Color"), ("PrincipledVolume", "Emission Color")),
            (("PrincipledVolume", "Volume"), ("MaterialOutput", "Volume")),
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


def Create_or_reset_pointcloud_mesh_material(name: str):
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

    mat["category"] = "pointcloud_mesh"

    CreateNodes(
        node_kwargs=[
            [
                {
                    "type_id": "ShaderNodeBsdfPrincipled",
                    "label": "Principled BSDF",
                    "width": 2,
                    "input_defaults": {"Roughness": 1.0, "Emission Strength": 0.2},
                }
            ],
            [
                {
                    "type_id": "ShaderNodeOutputMaterial",
                    "label": "Material Output",
                }
            ],
        ],
        socket_kwargs=[],
        node_links=[
            (("PrincipledBSDF", "BSDF"), ("MaterialOutput", "Surface")),
        ],
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
        create_or_reset_callback=Create_or_reset_pointcloud_volume_material,
        nt=self.node_tree,
    )
