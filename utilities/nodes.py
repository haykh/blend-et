from typing import Any
import bpy


def CreateNodes(
    node_kwargs: list[list[dict[str, Any]]],
    socket_kwargs: list[dict[str, Any]],
    node_links: list[tuple[tuple[str, str | int], tuple[str, str | int]]],
    node_tree: bpy.types.NodeTree,
    clear: bool = True,
) -> dict[str, bpy.types.Node]:
    nodes = node_tree.nodes
    links = node_tree.links
    interface = node_tree.interface
    if clear:
        nodes.clear()
        links.clear()

    def _new_node(
        type_id: str,
        name: str | None = None,
        label: str | None = None,
        location: tuple[int, int] | None = None,
    ):
        if clear:
            n = nodes.new(type_id)
        else:
            n = nodes.get(name) if name else None
            if n is None:
                n = nodes.new(type_id)
        if name is not None:
            n.name = name
        if label is not None:
            n.label = label
        if location is not None:
            n.location = location
        return n

    def _new_link(a, b):
        if not b.links or all(l.from_socket is not a for l in b.links):
            links.new(a, b)

    all_nodes = {}

    wspace = 200
    hspace = 200

    rolling_w = 0
    for col in node_kwargs:
        rolling_h = 0
        default_w = 0
        for row in col:
            node_type_id = row.pop("type_id")
            node_label: str = row.pop("label")
            node_name: str = node_label.replace(" ", "")

            node_width = row.pop("width", 1)
            if node_width > default_w:
                default_w = node_width

            node_height = row.pop("height", 1)

            new_node = _new_node(
                node_type_id,
                node_name,
                node_label,
                (rolling_w, -rolling_h),
            )
            if (node_input_defaults := row.pop("input_defaults", None)) is not None:
                for input_name, default_value in node_input_defaults.items():
                    new_node.inputs[input_name].default_value = default_value

            if (extra := row.pop("extra", None)) is not None:
                extra(new_node)

            for attr, value in row.items():
                if hasattr(new_node, attr):
                    setattr(new_node, attr, value)
                else:
                    raise KeyError(
                        f"Attribute '{attr}' not found in node '{node_name}'"
                    )

            all_nodes[node_name] = new_node

            rolling_h += node_height * hspace

        rolling_w += default_w * wspace

    if len(socket_kwargs) > 0 and interface is not None:
        for socket in socket_kwargs:
            socket_name = socket.pop("name")
            socket_in_out = socket.pop("in_out")
            socket_type = socket.pop("type")
            if socket_name is None or socket_in_out is None or socket_type is None:
                raise ValueError(
                    "Socket kwargs must include name, in_out, and type"
                )
            new_socket = interface.new_socket(
                name=socket_name, in_out=socket_in_out, socket_type=socket_type
            )
            for attr, value in socket.items():
                if hasattr(new_socket, attr):
                    setattr(new_socket, attr, value)
                else:
                    raise KeyError(
                        f"Attribute '{attr}' not found in socket '{socket_name}'"
                    )
    else:
        raise ValueError("No socket kwargs provided or node tree has no interface")

    for link in node_links:
        a_id, b_id = link
        a_node_id, a_socket_id = a_id
        b_node_id, b_socket_id = b_id
        if a_node_id not in all_nodes:
            raise KeyError(f"Node '{a_node_id}' not found for linking")
        if b_node_id not in all_nodes:
            raise KeyError(f"Node '{b_node_id}' not found for linking")
        a_node = all_nodes[a_node_id]
        b_node = all_nodes[b_node_id]
        _new_link(a_node.outputs[a_socket_id], b_node.inputs[b_socket_id])

    return all_nodes
