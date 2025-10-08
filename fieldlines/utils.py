import bpy, bmesh
import numpy as np

from ..colormaps.data import (  # pyright: ignore[reportMissingImports]
    Resolve_cmap_id,
    Stops_for_colormap,
    Apply_stops_to_colorramp,
)


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
        if k not in "xyz":
            for var, norm in zip(
                ["color", "thickness"],
                [
                    lambda x: (
                        (x - np.min(v)) / (np.max(v) - np.min(v))
                        if np.max(v) > np.min(v)
                        else v
                    ),
                    lambda x: (x / np.max(v) if np.max(v) > 0 else v),
                ],
            ):
                attr_k = mesh.attributes.new(name=var, type="FLOAT", domain="POINT")
                for i in range(npoints):
                    attr_k.data[i].value = norm(float(v[i]))
        else:
            attr_k = mesh.attributes.new(name=k, type="FLOAT", domain="POINT")
            for i in range(npoints):
                attr_k.data[i].value = float(v[i])

    mesh.update()

    return obj, collection_


def Create_fieldline_mesh(
    context: bpy.types.Context,
    collection: bpy.types.Collection | None = None,
    i: int = 0,
):
    """Creates a new mesh object for fieldlines and links it to the specified collection."""
    if (scene := context.scene) is None:
        raise RuntimeError("No active scene found")
    if collection is None:
        collection_ = bpy.data.collections.new("Fieldlines")
        scene.collection.children.link(collection_)
    else:
        collection_ = collection

    mesh = bpy.data.meshes.new(f"FieldlineMesh_{i}")
    obj = bpy.data.objects.new(f"FieldlineObj_{i}", mesh)
    collection_.objects.link(obj)

    if (context.view_layer is None) or (context.view_layer.objects is None):
        raise RuntimeError("No active view layer found")
    context.view_layer.objects.active = obj
    obj.select_set(True)

    return obj, collection_


def Create_fieldline_geometry_node(
    obj: bpy.types.Object,
    raw_obj: bpy.types.Object,
    material: bpy.types.Material,
    context: bpy.types.Context,
):
    """Creates a geometry node setup for the fieldline object."""

    nt = bpy.data.node_groups.new(
        type="GeometryNodeTree", name=f"FieldlineGeometryNodes_{obj.name}"
    )
    if nt.interface is None:
        raise RuntimeError("Node tree interface is None")
    obj.modifiers.new(name="GeometryNodes", type="NODES")
    obj.modifiers["GeometryNodes"].node_group = nt

    nodes = nt.nodes
    links = nt.links

    def _new_node(nodes, type_id, name=None, label=None, location=None):
        n = nodes.new(type_id)
        if name is not None:
            n.name = name
        if label is not None:
            n.label = label
        if location is not None:
            n.location = location
        return n

    def _link_if_missing(a, b):
        if not b.links or all(l.from_socket is not a for l in b.links):
            links.new(a, b)

    nodes.clear()
    links.clear()

    group_input = _new_node(
        nodes, "NodeGroupInput", "GroupInput", "Group Input", (1100.0, -360.0)
    )
    radius_socket = nt.interface.new_socket(
        name="Radius", in_out="INPUT", socket_type="NodeSocketFloat"
    )
    radius_socket.min_value = 0.0
    radius_socket.max_value = 3.4028234663852886e38
    radius_socket.subtype = "DISTANCE"
    radius_socket.attribute_domain = "POINT"
    radius_socket.default_input = "VALUE"
    radius_socket.default_value = 0.01

    radius_modulate_socket = nt.interface.new_socket(
        name="ModulateRadius", in_out="INPUT", socket_type="NodeSocketBool"
    )
    radius_modulate_socket.default_value = True

    objinfo = _new_node(
        nodes,
        "GeometryNodeObjectInfo",
        "RawFieldlineInfo",
        "Raw Fieldline Info",
        (-200, 0),
    )

    index = _new_node(nodes, "GeometryNodeInputIndex", "Index", "Index", (-200, -300))
    xyz_attrs = {
        ax: _new_node(
            nodes,
            "GeometryNodeInputNamedAttribute",
            f"Attr_{ax}",
            f"Attr {ax.upper()}",
            (100, 100 - i * 200),
        )
        for i, ax in enumerate(["x", "y", "z", "color", "thickness"])
    }
    xyz_sample = {
        ax: _new_node(
            nodes,
            "GeometryNodeSampleIndex",
            f"Sample_{ax}",
            f"Sample {ax.upper()}",
            (300, 200 - i * 200),
        )
        for i, ax in enumerate(["x", "y", "z", "color", "thickness"])
    }
    combine_xyz = _new_node(
        nodes, "ShaderNodeCombineXYZ", "CombineXYZ", "Combine XYZ", (500, -100)
    )
    domain_size = _new_node(
        nodes,
        "GeometryNodeAttributeDomainSize",
        "DomainSize",
        "Domain Size",
        (300.0, 400.0),
    )
    points = _new_node(nodes, "GeometryNodePoints", "Points", "Points", (700, 0))

    points_to_curves = _new_node(
        nodes,
        "GeometryNodePointsToCurves",
        "PointsToCurves",
        "Points to Curves",
        (900, 0),
    )
    store_attr_color = _new_node(
        nodes,
        "GeometryNodeStoreNamedAttribute",
        "StoreAttrColor",
        "Store Attr Color",
        (1100, 0),
    )
    store_attr_radius = _new_node(
        nodes,
        "GeometryNodeStoreNamedAttribute",
        "StoreAttrRadius",
        "Store Attr Radius",
        (1300, 0),
    )
    curve_to_mesh_1 = _new_node(
        nodes,
        "GeometryNodeCurveToMesh",
        "CurveToMesh",
        "Curve to Mesh",
        (1500, 0),
    )
    mesh_to_curve = _new_node(
        nodes,
        "GeometryNodeMeshToCurve",
        "MeshToCurve",
        "Mesh to Curve",
        (1700, 0),
    )
    spline_type = _new_node(
        nodes,
        "GeometryNodeCurveSplineType",
        "SplineType",
        "Spline Type",
        (1900, 0),
    )
    handle_type = _new_node(
        nodes,
        "GeometryNodeCurveSetHandles",
        "HandleType",
        "Handle Type",
        (2100, 0),
    )
    curve_to_mesh_2 = _new_node(
        nodes,
        "GeometryNodeCurveToMesh",
        "CurveToMeshFinal",
        "Curve to Mesh Final",
        (2300, 0),
    )
    circle_profile = _new_node(
        nodes,
        "GeometryNodeCurvePrimitiveCircle",
        "CircleProfile",
        "Circle Profile",
        (2000.0, -300.0),
    )
    set_material = _new_node(
        nodes, "GeometryNodeSetMaterial", "SetMaterial", "Set Material", (2480.0, 0.0)
    )

    group_output = _new_node(
        nodes, "NodeGroupOutput", "GroupOutput", "Group Output", (2660.0, 0.0)
    )
    group_output.is_active_output = True

    geometry_output = nt.interface.new_socket(
        name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry"
    )

    radius_attr = _new_node(
        nodes,
        "GeometryNodeInputNamedAttribute",
        "AttrRadius",
        "Attr Radius",
        (1900.0, 280.0),
    )
    radius_attr.data_type = "FLOAT"
    radius_attr.inputs[0].default_value = "thickness"

    radius_index = _new_node(
        nodes, "GeometryNodeInputIndex", "RadiusIndex", "Radius Index", (1900.0, 120.0)
    )

    radius_sample = _new_node(
        nodes,
        "GeometryNodeSampleIndex",
        "SampleRadius",
        "Sample radius",
        (2100.0, 220.0),
    )
    radius_sample.data_type = "FLOAT"
    radius_sample.domain = "POINT"

    radius_switch = _new_node(
        nodes, "GeometryNodeSwitch", "RadiusSwitch", "Radius Switch", (2000.0, -140.0)
    )
    radius_switch.input_type = "FLOAT"
    radius_switch.inputs["False"].default_value = 1.0

    for ax in ["x", "y", "z", "color", "thickness"]:
        xyz_attrs[ax].data_type = "FLOAT"
        xyz_attrs[ax].inputs[0].default_value = ax
        xyz_sample[ax].data_type = "FLOAT"
        xyz_sample[ax].domain = "POINT"
        _link_if_missing(objinfo.outputs["Geometry"], xyz_sample[ax].inputs["Geometry"])
        _link_if_missing(index.outputs["Index"], xyz_sample[ax].inputs["Index"])
        _link_if_missing(
            xyz_attrs[ax].outputs["Attribute"], xyz_sample[ax].inputs["Value"]
        )

    for ax in "xyz":
        _link_if_missing(
            xyz_sample[ax].outputs["Value"], combine_xyz.inputs[ax.upper()]
        )

    _link_if_missing(objinfo.outputs["Geometry"], domain_size.inputs["Geometry"])
    _link_if_missing(domain_size.outputs["Point Count"], points.inputs["Count"])
    _link_if_missing(combine_xyz.outputs["Vector"], points.inputs["Position"])
    _link_if_missing(points.outputs["Points"], points_to_curves.inputs["Points"])

    _link_if_missing(
        points_to_curves.outputs["Curves"], store_attr_color.inputs["Geometry"]
    )
    store_attr_color.data_type = "FLOAT"
    store_attr_color.domain = "POINT"
    store_attr_color.inputs["Name"].default_value = "color"
    _link_if_missing(
        xyz_sample["color"].outputs["Value"], store_attr_color.inputs["Value"]
    )

    _link_if_missing(
        store_attr_color.outputs["Geometry"], store_attr_radius.inputs["Geometry"]
    )
    store_attr_radius.data_type = "FLOAT"
    store_attr_radius.domain = "POINT"
    store_attr_radius.inputs["Name"].default_value = "thickness"

    _link_if_missing(
        xyz_sample["thickness"].outputs["Value"], store_attr_radius.inputs["Value"]
    )
    _link_if_missing(
        store_attr_radius.outputs["Geometry"], curve_to_mesh_1.inputs["Curve"]
    )
    _link_if_missing(curve_to_mesh_1.outputs["Mesh"], mesh_to_curve.inputs["Mesh"])
    _link_if_missing(mesh_to_curve.outputs["Curve"], spline_type.inputs["Curve"])
    spline_type.spline_type = "BEZIER"
    _link_if_missing(spline_type.outputs["Curve"], handle_type.inputs["Curve"])
    handle_type.handle_type = "AUTO"
    handle_type.mode = {"LEFT", "RIGHT"}
    _link_if_missing(handle_type.outputs["Curve"], curve_to_mesh_2.inputs["Curve"])
    _link_if_missing(
        circle_profile.outputs["Curve"], curve_to_mesh_2.inputs["Profile Curve"]
    )
    circle_profile.mode = "RADIUS"
    _link_if_missing(group_input.outputs["Radius"], circle_profile.inputs["Radius"])
    _link_if_missing(curve_to_mesh_2.outputs["Mesh"], set_material.inputs["Geometry"])
    set_material.inputs["Material"].default_value = material
    _link_if_missing(set_material.outputs["Geometry"], group_output.inputs[0])

    _link_if_missing(radius_attr.outputs["Attribute"], radius_sample.inputs["Value"])
    _link_if_missing(radius_index.outputs["Index"], radius_sample.inputs["Index"])
    _link_if_missing(spline_type.outputs["Curve"], radius_sample.inputs["Geometry"])
    _link_if_missing(radius_sample.outputs["Value"], radius_switch.inputs["True"])
    _link_if_missing(radius_switch.outputs["Output"], curve_to_mesh_2.inputs["Scale"])
    _link_if_missing(
        group_input.outputs["ModulateRadius"], radius_switch.inputs["Switch"]
    )

    objinfo.inputs["Object"].default_value = raw_obj

    return nt


def Create_fieldline_controller(collection: bpy.types.Collection):
    if "Radius" not in collection.keys():
        collection["Radius"] = 0.01
    ui = collection.id_properties_ui("Radius")
    ui.update(min=0.0, soft_min=0.0, soft_max=1.0, description="Fieldline radius")

    if "ModulateRadius" not in collection.keys():
        collection["ModulateRadius"] = True
    ui = collection.id_properties_ui("ModulateRadius")
    ui.update(description="Modulate fieldline radii")

    # Helpers
    def gn_modifiers(obj):
        return [
            m
            for m in obj.modifiers
            if m.type == "NODES" and getattr(m, "node_group", None) is not None
        ]

    def keys_from_interface(name, gn_mod):
        candidates = [name]
        ng = getattr(gn_mod, "node_group", None)
        if ng and hasattr(ng, "interface"):
            try:
                for item in ng.interface.items_tree:
                    if getattr(item, "name", None) == name:
                        ident = getattr(item, "identifier", None)
                        if ident:
                            candidates.append(ident)
                            candidates.append(f"Input_{ident}")
            except Exception:
                pass

        seen, dedup = set(), []
        for k in candidates:
            if k not in seen:
                seen.add(k)
                dedup.append(k)
        return dedup

    def add_driver_to(gn_mod, target_coll, prop_name):
        candidates = keys_from_interface(prop_name, gn_mod)
        present = [k for k in candidates if k in gn_mod.keys()]
        if not present:
            return False

        key = present[0]
        data_path = f'["{key}"]'

        # Remove any existing driver first
        try:
            gn_mod.driver_remove(data_path)
        except Exception:
            pass

        drv = gn_mod.driver_add(data_path).driver
        drv.type = "SCRIPTED"

        # Clear variables (avoid duplicates if re-running)
        while drv.variables:
            drv.variables.remove(drv.variables[0])

        v = drv.variables.new()
        v.name = "x"
        v.type = "SINGLE_PROP"
        t = v.targets[0]
        t.id_type = "COLLECTION"  # <-- set id_type first
        t.id = target_coll  # <-- now assigning the Collection is valid
        t.data_path = f'["{prop_name}"]'

        drv.expression = "x"
        return True

    # Wire up all GN modifiers in the collection to the collection properties
    for obj in collection.objects:
        for gn_mod in gn_modifiers(obj):
            for prop in ["Radius", "ModulateRadius"]:
                if not add_driver_to(gn_mod, collection, prop):
                    raise RuntimeError(
                        f"Could not bind '{prop}' for {obj.name} (modifier {gn_mod.name})"
                    )


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
