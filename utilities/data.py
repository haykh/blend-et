import bpy
import bmesh
import numpy as np


def Encode_raw_data(
    data: dict[str, list[float] | np.ndarray],
    context: bpy.types.Context,
    collection: bpy.types.Collection | None = None,
    prefix: str = "",
    suffix: str = "",
) -> tuple[bpy.types.Object, bpy.types.Collection]:
    """Encodes a dictionary of arrays as a mesh with point attributes."""
    if (scene := context.scene) is None:
        raise RuntimeError("No active scene found")

    npoints = len(data[list(data.keys())[0]])
    assert all(
        len(v) == npoints for v in data.values()
    ), "Not all arrays have equal lengths"

    if collection is None:
        collection_ = bpy.data.collections.new(f"{prefix}Raw{suffix}")
        scene.collection.children.link(collection_)
    else:
        collection_ = collection
    collection_.hide_viewport = True
    collection_.hide_render = True

    def _find_layer_collection(layer_coll, target_coll):
        if layer_coll.collection == target_coll:
            return layer_coll
        for ch in layer_coll.children:
            f = _find_layer_collection(ch, target_coll)
            if f:
                return f
        return None

    for vl in scene.view_layers:
        if lc := _find_layer_collection(vl.layer_collection, collection_):
            lc.exclude = True

    mesh = bpy.data.meshes.new(f"{prefix}RawMesh{suffix}")
    obj = bpy.data.objects.new(f"{prefix}RawObj{suffix}", mesh)
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
