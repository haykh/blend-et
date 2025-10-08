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
        norm = lambda x: x
        if k not in "xyz":
            norm = lambda x: (
                (x - np.min(v)) / (np.max(v) - np.min(v))
                if np.max(v) > np.min(v)
                else v
            )
        attr_k = mesh.attributes.new(name=k, type="FLOAT", domain="POINT")
        for i in range(npoints):
            attr_k.data[i].value = norm(float(v[i]))

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
        nodes, "NodeGroupInput", "GroupInput", "Group Input", (-200, -700)
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
        for i, ax in enumerate("xyzt")
    }
    xyz_sample = {
        ax: _new_node(
            nodes,
            "GeometryNodeSampleIndex",
            f"Sample_{ax}",
            f"Sample {ax.upper()}",
            (300, 200 - i * 200),
        )
        for i, ax in enumerate("xyzt")
    }
    combine_xyz = _new_node(
        nodes, "ShaderNodeCombineXYZ", "CombineXYZ", "Combine XYZ", (500, -100)
    )
    domain_size = _new_node(
        nodes,
        "GeometryNodeAttributeDomainSize",
        "DomainSize",
        "Domain Size",
        (300, -600),
    )
    points = _new_node(nodes, "GeometryNodePoints", "Points", "Points", (700, 0))

    points_to_curves = _new_node(
        nodes,
        "GeometryNodePointsToCurves",
        "PointsToCurves",
        "Points to Curves",
        (900, 0),
    )
    store_attr_t = _new_node(
        nodes,
        "GeometryNodeStoreNamedAttribute",
        "StoreAttrT",
        "Store Attr t",
        (1100, 0),
    )
    curve_to_mesh_1 = _new_node(
        nodes,
        "GeometryNodeCurveToMesh",
        "CurveToMesh",
        "Curve to Mesh",
        (1300, 0),
    )
    mesh_to_curve = _new_node(
        nodes,
        "GeometryNodeMeshToCurve",
        "MeshToCurve",
        "Mesh to Curve",
        (1500, 0),
    )
    spline_type = _new_node(
        nodes,
        "GeometryNodeCurveSplineType",
        "SplineType",
        "Spline Type",
        (1700, 0),
    )
    handle_type = _new_node(
        nodes,
        "GeometryNodeCurveSetHandles",
        "HandleType",
        "Handle Type",
        (1900, 0),
    )
    curve_to_mesh_2 = _new_node(
        nodes,
        "GeometryNodeCurveToMesh",
        "CurveToMeshFinal",
        "Curve to Mesh Final",
        (2100, 0),
    )
    circle_profile = _new_node(
        nodes,
        "GeometryNodeCurvePrimitiveCircle",
        "CircleProfile",
        "Circle Profile",
        (1900, -300),
    )
    set_material = _new_node(
        nodes, "GeometryNodeSetMaterial", "SetMaterial", "Set Material", (2200, 0)
    )

    group_output = _new_node(
        nodes, "NodeGroupOutput", "GroupOutput", "Group Output", (2600, 0)
    )
    group_output.is_active_output = True

    geometry_output = nt.interface.new_socket(
        name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry"
    )

    for ax in "xyzt":
        xyz_attrs[ax].data_type = "FLOAT"
        xyz_attrs[ax].inputs[0].default_value = ax if ax != "t" else "mag"
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
        points_to_curves.outputs["Curves"], store_attr_t.inputs["Geometry"]
    )
    store_attr_t.data_type = "FLOAT"
    store_attr_t.domain = "POINT"
    store_attr_t.inputs["Name"].default_value = "mag"

    _link_if_missing(xyz_sample["t"].outputs["Value"], store_attr_t.inputs["Value"])
    _link_if_missing(store_attr_t.outputs["Geometry"], curve_to_mesh_1.inputs["Curve"])
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

    objinfo.inputs["Object"].default_value = raw_obj

    RADIUS_VALUE = 0.01
    modifier = obj.modifiers.get("GeometryNodes")
    if modifier and modifier.node_group is nt:
        if ident := getattr(radius_socket, "identifier", None):
            modifier[ident] = RADIUS_VALUE

    return nt


def Create_fieldline_controller(collection: bpy.types.Collection):
    controller = bpy.data.objects.get("FieldlineController")
    if controller is None:
        controller = bpy.data.objects.new("FieldlineController", None)
        controller.empty_display_type = "SPHERE"
        collection.objects.link(controller)

    if "Radius" not in controller.keys():
        controller["Radius"] = 0.01
        ui = controller.id_properties_ui("Radius")
        ui.update(min=0.0, soft_min=0.0, soft_max=1.0, description="Master Radius")

    def gn_modifiers(obj):
        return [
            m
            for m in obj.modifiers
            if m.type == "NODES" and getattr(m, "node_group", None) is not None
        ]

    def radius_keys_from_interface(gn_mod):
        candidates = ["Radius"]

        ng = getattr(gn_mod, "node_group", None)
        if ng and hasattr(ng, "interface"):
            try:
                for item in ng.interface.items_tree:
                    if getattr(item, "name", None) == "Radius":
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

    def add_driver_to_radius(gn_mod, controller, prop_name="Radius"):
        candidates = radius_keys_from_interface(gn_mod)
        present = [k for k in candidates if k in gn_mod.keys()]
        if not present:
            return False

        key = present[0]
        data_path = f'["{key}"]'

        try:
            gn_mod.driver_remove(data_path)
        except:
            pass

        drv = gn_mod.driver_add(data_path).driver
        drv.type = "SCRIPTED"
        v = drv.variables.new()
        v.name = "x"
        v.targets[0].id = controller
        v.targets[0].data_path = f'["{prop_name}"]'
        drv.expression = "x"
        return True

    for obj in collection.objects:
        if obj == controller:
            continue
        for gn_mod in gn_modifiers(obj):
            if not add_driver_to_radius(gn_mod, controller, "Radius"):
                raise RuntimeError(
                    f"Could not bind 'Radius' for {obj.name} (modifier {gn_mod.name})"
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
    attr_node.attribute_name = "mag"

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
