import bpy


def Axes_grid_geometry_node():
    def divider_node_group():
        """Initialize divider node group"""
        divider = bpy.data.node_groups.new(type="GeometryNodeTree", name="Divider")

        divider.color_tag = "NONE"
        divider.description = ""
        divider.default_group_node_width = 140

        # divider interface

        # Socket IntPart
        intpart_socket = divider.interface.new_socket(
            name="IntPart", in_out="OUTPUT", socket_type="NodeSocketInt"
        )
        intpart_socket.default_value = 0
        intpart_socket.min_value = -2147483648
        intpart_socket.max_value = 2147483647
        intpart_socket.subtype = "NONE"
        intpart_socket.attribute_domain = "POINT"
        intpart_socket.default_input = "VALUE"

        # Socket Remainder
        remainder_socket = divider.interface.new_socket(
            name="Remainder", in_out="OUTPUT", socket_type="NodeSocketFloat"
        )
        remainder_socket.default_value = 0.0
        remainder_socket.min_value = -3.4028234663852886e38
        remainder_socket.max_value = 3.4028234663852886e38
        remainder_socket.subtype = "NONE"
        remainder_socket.attribute_domain = "POINT"
        remainder_socket.default_input = "VALUE"

        # Socket Size
        size_socket = divider.interface.new_socket(
            name="Size", in_out="INPUT", socket_type="NodeSocketFloat"
        )
        size_socket.default_value = 0.0
        size_socket.min_value = -3.4028234663852886e38
        size_socket.max_value = 3.4028234663852886e38
        size_socket.subtype = "DISTANCE"
        size_socket.attribute_domain = "POINT"
        size_socket.default_input = "VALUE"

        # Socket Delta
        delta_socket = divider.interface.new_socket(
            name="Delta", in_out="INPUT", socket_type="NodeSocketFloat"
        )
        delta_socket.default_value = 0.0
        delta_socket.min_value = -3.4028234663852886e38
        delta_socket.max_value = 3.4028234663852886e38
        delta_socket.subtype = "DISTANCE"
        delta_socket.attribute_domain = "POINT"
        delta_socket.default_input = "VALUE"

        # Socket MinCutoff
        mincutoff_socket = divider.interface.new_socket(
            name="MinCutoff", in_out="INPUT", socket_type="NodeSocketFloat"
        )
        mincutoff_socket.default_value = 1000.0
        mincutoff_socket.min_value = -10000.0
        mincutoff_socket.max_value = 10000.0
        mincutoff_socket.subtype = "NONE"
        mincutoff_socket.attribute_domain = "POINT"
        mincutoff_socket.default_input = "VALUE"

        # Initialize divider nodes

        # Node Group Output
        group_output = divider.nodes.new("NodeGroupOutput")
        group_output.name = "Group Output"
        group_output.is_active_output = True

        # Node Group Input
        group_input = divider.nodes.new("NodeGroupInput")
        group_input.name = "Group Input"

        # Node Math
        math = divider.nodes.new("ShaderNodeMath")
        math.name = "Math"
        math.operation = "DIVIDE"
        math.use_clamp = False

        # Node Math.001
        math_001 = divider.nodes.new("ShaderNodeMath")
        math_001.name = "Math.001"
        math_001.operation = "DIVIDE"
        math_001.use_clamp = False

        # Node Math.002
        math_002 = divider.nodes.new("ShaderNodeMath")
        math_002.name = "Math.002"
        math_002.operation = "MAXIMUM"
        math_002.use_clamp = False

        # Node Float to Integer
        float_to_integer = divider.nodes.new("FunctionNodeFloatToInt")
        float_to_integer.name = "Float to Integer"
        float_to_integer.rounding_mode = "FLOOR"

        # Node Math.003
        math_003 = divider.nodes.new("ShaderNodeMath")
        math_003.name = "Math.003"
        math_003.operation = "MULTIPLY"
        math_003.use_clamp = False

        # Node Math.004
        math_004 = divider.nodes.new("ShaderNodeMath")
        math_004.name = "Math.004"
        math_004.operation = "SUBTRACT"
        math_004.use_clamp = False

        # Node Reroute.001
        reroute_001 = divider.nodes.new("NodeReroute")
        reroute_001.name = "Reroute.001"
        reroute_001.socket_idname = "NodeSocketFloatDistance"
        # Node Reroute
        reroute = divider.nodes.new("NodeReroute")
        reroute.name = "Reroute"
        reroute.socket_idname = "NodeSocketFloatDistance"
        # Set locations
        group_output.location = (534.4945068359375, 158.3688507080078)
        group_input.location = (-644.4876708984375, 13.37038803100586)
        math.location = (-48.77610778808594, 101.22575378417969)
        math_001.location = (-399.30419921875, 142.0231475830078)
        math_002.location = (-223.39283752441406, 10.690231323242188)
        float_to_integer.location = (149.7301483154297, 206.2631072998047)
        math_003.location = (151.51754760742188, 59.11619567871094)
        math_004.location = (328.94659423828125, 97.56404113769531)
        reroute_001.location = (-326.7369384765625, -206.2631072998047)
        reroute.location = (-328.94659423828125, -118.35302734375)

        # Set dimensions
        group_output.width, group_output.height = 140.0, 100.0
        group_input.width, group_input.height = 140.0, 100.0
        math.width, math.height = 140.0, 100.0
        math_001.width, math_001.height = 140.0, 100.0
        math_002.width, math_002.height = 140.0, 100.0
        float_to_integer.width, float_to_integer.height = 140.0, 100.0
        math_003.width, math_003.height = 140.0, 100.0
        math_004.width, math_004.height = 140.0, 100.0
        reroute_001.width, reroute_001.height = 10.0, 100.0
        reroute.width, reroute.height = 10.0, 100.0

        # Initialize divider links

        # float_to_integer.Integer -> math_003.Value
        divider.links.new(float_to_integer.outputs[0], math_003.inputs[1])
        # reroute_001.Output -> math_002.Value
        divider.links.new(reroute_001.outputs[0], math_002.inputs[1])
        # math_001.Value -> math_002.Value
        divider.links.new(math_001.outputs[0], math_002.inputs[0])
        # reroute.Output -> math_001.Value
        divider.links.new(reroute.outputs[0], math_001.inputs[0])
        # reroute_001.Output -> math_003.Value
        divider.links.new(reroute_001.outputs[0], math_003.inputs[0])
        # reroute.Output -> math.Value
        divider.links.new(reroute.outputs[0], math.inputs[0])
        # math.Value -> float_to_integer.Float
        divider.links.new(math.outputs[0], float_to_integer.inputs[0])
        # reroute.Output -> math_004.Value
        divider.links.new(reroute.outputs[0], math_004.inputs[0])
        # math_003.Value -> math_004.Value
        divider.links.new(math_003.outputs[0], math_004.inputs[1])
        # math_002.Value -> math.Value
        divider.links.new(math_002.outputs[0], math.inputs[1])
        # group_input.Size -> reroute.Input
        divider.links.new(group_input.outputs[0], reroute.inputs[0])
        # group_input.Delta -> reroute_001.Input
        divider.links.new(group_input.outputs[1], reroute_001.inputs[0])
        # float_to_integer.Integer -> group_output.IntPart
        divider.links.new(float_to_integer.outputs[0], group_output.inputs[0])
        # math_004.Value -> group_output.Remainder
        divider.links.new(math_004.outputs[0], group_output.inputs[1])
        # group_input.MinCutoff -> math_001.Value
        divider.links.new(group_input.outputs[2], math_001.inputs[1])

        return divider

    divider = divider_node_group()

    def generatepoints_node_group():
        """Initialize generatepoints node group"""
        generatepoints = bpy.data.node_groups.new(
            type="GeometryNodeTree", name="GeneratePoints"
        )

        generatepoints.color_tag = "NONE"
        generatepoints.description = ""
        generatepoints.default_group_node_width = 140

        # generatepoints interface

        # Socket Points
        points_socket = generatepoints.interface.new_socket(
            name="Points", in_out="OUTPUT", socket_type="NodeSocketGeometry"
        )
        points_socket.attribute_domain = "POINT"
        points_socket.default_input = "VALUE"

        # Socket Xmin
        xmin_socket = generatepoints.interface.new_socket(
            name="Xmin", in_out="OUTPUT", socket_type="NodeSocketFloat"
        )
        xmin_socket.default_value = 0.0
        xmin_socket.min_value = -3.4028234663852886e38
        xmin_socket.max_value = 3.4028234663852886e38
        xmin_socket.subtype = "NONE"
        xmin_socket.attribute_domain = "POINT"
        xmin_socket.default_input = "VALUE"

        # Socket Xmax
        xmax_socket = generatepoints.interface.new_socket(
            name="Xmax", in_out="OUTPUT", socket_type="NodeSocketFloat"
        )
        xmax_socket.default_value = 0.0
        xmax_socket.min_value = -3.4028234663852886e38
        xmax_socket.max_value = 3.4028234663852886e38
        xmax_socket.subtype = "NONE"
        xmax_socket.attribute_domain = "POINT"
        xmax_socket.default_input = "VALUE"

        # Socket Size
        size_socket_1 = generatepoints.interface.new_socket(
            name="Size", in_out="INPUT", socket_type="NodeSocketFloat"
        )
        size_socket_1.default_value = 0.0
        size_socket_1.min_value = -3.4028234663852886e38
        size_socket_1.max_value = 3.4028234663852886e38
        size_socket_1.subtype = "DISTANCE"
        size_socket_1.attribute_domain = "POINT"
        size_socket_1.default_input = "VALUE"

        # Socket Delta
        delta_socket_1 = generatepoints.interface.new_socket(
            name="Delta", in_out="INPUT", socket_type="NodeSocketFloat"
        )
        delta_socket_1.default_value = 0.0
        delta_socket_1.min_value = -3.4028234663852886e38
        delta_socket_1.max_value = 3.4028234663852886e38
        delta_socket_1.subtype = "DISTANCE"
        delta_socket_1.attribute_domain = "POINT"
        delta_socket_1.default_input = "VALUE"

        # Initialize generatepoints nodes

        # Node Group Output
        group_output_1 = generatepoints.nodes.new("NodeGroupOutput")
        group_output_1.name = "Group Output"
        group_output_1.is_active_output = True

        # Node Group Input
        group_input_1 = generatepoints.nodes.new("NodeGroupInput")
        group_input_1.name = "Group Input"

        # Node Group
        group = generatepoints.nodes.new("GeometryNodeGroup")
        group.label = "Divider"
        group.name = "Group"
        group.node_tree = divider
        # Socket_4
        group.inputs[2].default_value = 1000.0

        # Node Grid
        grid = generatepoints.nodes.new("GeometryNodeMeshGrid")
        grid.name = "Grid"
        # Size X
        grid.inputs[0].default_value = 1.0
        # Size Y
        grid.inputs[1].default_value = 0.0
        # Vertices Y
        grid.inputs[3].default_value = 1

        # Node Mesh to Points
        mesh_to_points = generatepoints.nodes.new("GeometryNodeMeshToPoints")
        mesh_to_points.name = "Mesh to Points"
        mesh_to_points.mode = "VERTICES"
        # Selection
        mesh_to_points.inputs[1].default_value = True
        # Radius
        mesh_to_points.inputs[3].default_value = 0.05000000074505806

        # Node Points
        points = generatepoints.nodes.new("GeometryNodePoints")
        points.name = "Points"
        # Count
        points.inputs[0].default_value = 1
        # Radius
        points.inputs[2].default_value = 0.05000000074505806

        # Node Combine XYZ
        combine_xyz = generatepoints.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz.name = "Combine XYZ"
        # Y
        combine_xyz.inputs[1].default_value = 0.0
        # Z
        combine_xyz.inputs[2].default_value = 0.0

        # Node Math.002
        math_002_1 = generatepoints.nodes.new("ShaderNodeMath")
        math_002_1.name = "Math.002"
        math_002_1.operation = "MULTIPLY"
        math_002_1.use_clamp = False

        # Node Index
        index = generatepoints.nodes.new("GeometryNodeInputIndex")
        index.name = "Index"

        # Node Combine XYZ.001
        combine_xyz_001 = generatepoints.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_001.name = "Combine XYZ.001"
        # Y
        combine_xyz_001.inputs[1].default_value = 0.0
        # Z
        combine_xyz_001.inputs[2].default_value = 0.0

        # Node Join Geometry
        join_geometry = generatepoints.nodes.new("GeometryNodeJoinGeometry")
        join_geometry.name = "Join Geometry"

        # Node Compare
        compare = generatepoints.nodes.new("FunctionNodeCompare")
        compare.name = "Compare"
        compare.hide = True
        compare.data_type = "FLOAT"
        compare.mode = "ELEMENT"
        compare.operation = "GREATER_THAN"
        # B
        compare.inputs[1].default_value = 0.0

        # Node Switch
        switch = generatepoints.nodes.new("GeometryNodeSwitch")
        switch.name = "Switch"
        switch.input_type = "GEOMETRY"

        # Node Integer Math
        integer_math = generatepoints.nodes.new("FunctionNodeIntegerMath")
        integer_math.name = "Integer Math"
        integer_math.operation = "ADD"
        # Value_001
        integer_math.inputs[1].default_value = 1

        # Node Reroute
        reroute_1 = generatepoints.nodes.new("NodeReroute")
        reroute_1.name = "Reroute"
        reroute_1.socket_idname = "NodeSocketFloatDistance"
        # Node Reroute.001
        reroute_001_1 = generatepoints.nodes.new("NodeReroute")
        reroute_001_1.name = "Reroute.001"
        reroute_001_1.socket_idname = "NodeSocketFloatDistance"
        # Node Bounding Box
        bounding_box = generatepoints.nodes.new("GeometryNodeBoundBox")
        bounding_box.name = "Bounding Box"
        if bpy.app.version >= (4, 5, 0):
            # Use Radius
            bounding_box.inputs[1].default_value = False

        # Node Separate XYZ
        separate_xyz = generatepoints.nodes.new("ShaderNodeSeparateXYZ")
        separate_xyz.name = "Separate XYZ"

        # Node Separate XYZ.001
        separate_xyz_001 = generatepoints.nodes.new("ShaderNodeSeparateXYZ")
        separate_xyz_001.name = "Separate XYZ.001"

        # Set locations
        group_output_1.location = (955.1275024414062, -6.419400215148926)
        group_input_1.location = (-923.3380126953125, -29.36124610900879)
        group.location = (-554.2770385742188, 88.59540557861328)
        grid.location = (-7.6020660400390625, 232.83706665039062)
        mesh_to_points.location = (366.400390625, 173.43344116210938)
        points.location = (113.16140747070312, -174.24945068359375)
        combine_xyz.location = (83.83116149902344, 29.891265869140625)
        math_002_1.location = (-94.84319305419922, 16.159820556640625)
        index.location = (-268.221435546875, -96.43792724609375)
        combine_xyz_001.location = (-89.02586364746094, -232.8370819091797)
        join_geometry.location = (605.859130859375, 27.300506591796875)
        compare.location = (109.41166687011719, -134.76242065429688)
        switch.location = (306.04803466796875, -55.12001037597656)
        integer_math.location = (-367.06854248046875, 156.28042602539062)
        reroute_1.location = (-608.9279174804688, -81.63848876953125)
        reroute_001_1.location = (-618.570556640625, -60.04690170288086)
        bounding_box.location = (510.17449951171875, -95.80555725097656)
        separate_xyz.location = (733.577880859375, -55.14933776855469)
        separate_xyz_001.location = (733.577880859375, -186.74710083007812)

        # Set dimensions
        group_output_1.width, group_output_1.height = 140.0, 100.0
        group_input_1.width, group_input_1.height = 140.0, 100.0
        group.width, group.height = 168.23040771484375, 100.0
        grid.width, grid.height = 140.0, 100.0
        mesh_to_points.width, mesh_to_points.height = 140.0, 100.0
        points.width, points.height = 140.0, 100.0
        combine_xyz.width, combine_xyz.height = 140.0, 100.0
        math_002_1.width, math_002_1.height = 140.0, 100.0
        index.width, index.height = 140.0, 100.0
        combine_xyz_001.width, combine_xyz_001.height = 140.0, 100.0
        join_geometry.width, join_geometry.height = 140.0, 100.0
        compare.width, compare.height = 140.0, 100.0
        switch.width, switch.height = 140.0, 100.0
        integer_math.width, integer_math.height = 140.0, 100.0
        reroute_1.width, reroute_1.height = 10.0, 100.0
        reroute_001_1.width, reroute_001_1.height = 10.0, 100.0
        bounding_box.width, bounding_box.height = 140.0, 100.0
        separate_xyz.width, separate_xyz.height = 140.0, 100.0
        separate_xyz_001.width, separate_xyz_001.height = 140.0, 100.0

        # Initialize generatepoints links

        # combine_xyz.Vector -> mesh_to_points.Position
        generatepoints.links.new(combine_xyz.outputs[0], mesh_to_points.inputs[2])
        # reroute_1.Output -> group.Delta
        generatepoints.links.new(reroute_1.outputs[0], group.inputs[1])
        # math_002_1.Value -> combine_xyz.X
        generatepoints.links.new(math_002_1.outputs[0], combine_xyz.inputs[0])
        # points.Points -> switch.True
        generatepoints.links.new(points.outputs[0], switch.inputs[2])
        # index.Index -> math_002_1.Value
        generatepoints.links.new(index.outputs[0], math_002_1.inputs[1])
        # integer_math.Value -> grid.Vertices X
        generatepoints.links.new(integer_math.outputs[0], grid.inputs[2])
        # group.Remainder -> compare.A
        generatepoints.links.new(group.outputs[1], compare.inputs[0])
        # switch.Output -> join_geometry.Geometry
        generatepoints.links.new(switch.outputs[0], join_geometry.inputs[0])
        # compare.Result -> switch.Switch
        generatepoints.links.new(compare.outputs[0], switch.inputs[0])
        # reroute_001_1.Output -> group.Size
        generatepoints.links.new(reroute_001_1.outputs[0], group.inputs[0])
        # reroute_1.Output -> math_002_1.Value
        generatepoints.links.new(reroute_1.outputs[0], math_002_1.inputs[0])
        # combine_xyz_001.Vector -> points.Position
        generatepoints.links.new(combine_xyz_001.outputs[0], points.inputs[1])
        # grid.Mesh -> mesh_to_points.Mesh
        generatepoints.links.new(grid.outputs[0], mesh_to_points.inputs[0])
        # group.IntPart -> integer_math.Value
        generatepoints.links.new(group.outputs[0], integer_math.inputs[0])
        # reroute_001_1.Output -> combine_xyz_001.X
        generatepoints.links.new(reroute_001_1.outputs[0], combine_xyz_001.inputs[0])
        # group_input_1.Size -> reroute_001_1.Input
        generatepoints.links.new(group_input_1.outputs[0], reroute_001_1.inputs[0])
        # group_input_1.Delta -> reroute_1.Input
        generatepoints.links.new(group_input_1.outputs[1], reroute_1.inputs[0])
        # join_geometry.Geometry -> group_output_1.Points
        generatepoints.links.new(join_geometry.outputs[0], group_output_1.inputs[0])
        # join_geometry.Geometry -> bounding_box.Geometry
        generatepoints.links.new(join_geometry.outputs[0], bounding_box.inputs[0])
        # separate_xyz.X -> group_output_1.Xmin
        generatepoints.links.new(separate_xyz.outputs[0], group_output_1.inputs[1])
        # bounding_box.Min -> separate_xyz.Vector
        generatepoints.links.new(bounding_box.outputs[1], separate_xyz.inputs[0])
        # bounding_box.Max -> separate_xyz_001.Vector
        generatepoints.links.new(bounding_box.outputs[2], separate_xyz_001.inputs[0])
        # separate_xyz_001.X -> group_output_1.Xmax
        generatepoints.links.new(separate_xyz_001.outputs[0], group_output_1.inputs[2])
        # mesh_to_points.Points -> join_geometry.Geometry
        generatepoints.links.new(mesh_to_points.outputs[0], join_geometry.inputs[0])

        return generatepoints

    generatepoints = generatepoints_node_group()

    def ticks_node_group():
        """Initialize ticks node group"""
        ticks = bpy.data.node_groups.new(type="GeometryNodeTree", name="Ticks")

        ticks.color_tag = "NONE"
        ticks.description = ""
        ticks.default_group_node_width = 140

        # ticks interface

        # Socket Geometry
        geometry_socket = ticks.interface.new_socket(
            name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry"
        )
        geometry_socket.attribute_domain = "POINT"
        geometry_socket.default_input = "VALUE"

        # Socket Size
        size_socket_2 = ticks.interface.new_socket(
            name="Size", in_out="INPUT", socket_type="NodeSocketFloat"
        )
        size_socket_2.default_value = 0.0
        size_socket_2.min_value = -3.4028234663852886e38
        size_socket_2.max_value = 3.4028234663852886e38
        size_socket_2.subtype = "DISTANCE"
        size_socket_2.attribute_domain = "POINT"
        size_socket_2.default_input = "VALUE"

        # Socket Delta
        delta_socket_2 = ticks.interface.new_socket(
            name="Delta", in_out="INPUT", socket_type="NodeSocketFloat"
        )
        delta_socket_2.default_value = 0.0
        delta_socket_2.min_value = -3.4028234663852886e38
        delta_socket_2.max_value = 3.4028234663852886e38
        delta_socket_2.subtype = "DISTANCE"
        delta_socket_2.attribute_domain = "POINT"
        delta_socket_2.default_input = "VALUE"

        # Initialize ticks nodes

        # Node Group Output
        group_output_2 = ticks.nodes.new("NodeGroupOutput")
        group_output_2.name = "Group Output"
        group_output_2.is_active_output = True

        # Node Group Input
        group_input_2 = ticks.nodes.new("NodeGroupInput")
        group_input_2.name = "Group Input"

        # Node Group.001
        group_001 = ticks.nodes.new("GeometryNodeGroup")
        group_001.label = "GeneratePoints"
        group_001.name = "Group.001"
        group_001.node_tree = generatepoints

        # Node Instance on Points
        instance_on_points = ticks.nodes.new("GeometryNodeInstanceOnPoints")
        instance_on_points.name = "Instance on Points"
        # Selection
        instance_on_points.inputs[1].default_value = True
        # Pick Instance
        instance_on_points.inputs[3].default_value = False
        # Instance Index
        instance_on_points.inputs[4].default_value = 0
        # Rotation
        instance_on_points.inputs[5].default_value = (-1.5707963705062866, 0.0, 0.0)
        # Scale
        instance_on_points.inputs[6].default_value = (1.0, 1.0, 1.0)

        # Node Curve Line
        curve_line = ticks.nodes.new("GeometryNodeCurvePrimitiveLine")
        curve_line.name = "Curve Line"
        curve_line.mode = "POINTS"
        # Start
        curve_line.inputs[0].default_value = (0.0, 0.0, 0.0)
        # End
        curve_line.inputs[1].default_value = (0.0, 0.0, 1.0)

        # Node Points
        points_1 = ticks.nodes.new("GeometryNodePoints")
        points_1.name = "Points"
        # Count
        points_1.inputs[0].default_value = 1
        # Radius
        points_1.inputs[2].default_value = 0.10000000149011612

        # Node Combine XYZ
        combine_xyz_1 = ticks.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_1.name = "Combine XYZ"
        # Y
        combine_xyz_1.inputs[1].default_value = 0.0
        # Z
        combine_xyz_1.inputs[2].default_value = 0.0

        # Node Join Geometry
        join_geometry_1 = ticks.nodes.new("GeometryNodeJoinGeometry")
        join_geometry_1.name = "Join Geometry"

        # Node Points.001
        points_001 = ticks.nodes.new("GeometryNodePoints")
        points_001.name = "Points.001"
        # Count
        points_001.inputs[0].default_value = 1
        # Radius
        points_001.inputs[2].default_value = 0.10000000149011612

        # Node Combine XYZ.001
        combine_xyz_001_1 = ticks.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_001_1.name = "Combine XYZ.001"
        # Y
        combine_xyz_001_1.inputs[1].default_value = 0.0
        # Z
        combine_xyz_001_1.inputs[2].default_value = 0.0

        # Node Points to Curves
        points_to_curves = ticks.nodes.new("GeometryNodePointsToCurves")
        points_to_curves.name = "Points to Curves"
        # Curve Group ID
        points_to_curves.inputs[1].default_value = 0
        # Weight
        points_to_curves.inputs[2].default_value = 0.0

        # Node Join Geometry.001
        join_geometry_001 = ticks.nodes.new("GeometryNodeJoinGeometry")
        join_geometry_001.name = "Join Geometry.001"

        # Node Set Position
        set_position = ticks.nodes.new("GeometryNodeSetPosition")
        set_position.name = "Set Position"
        # Selection
        set_position.inputs[1].default_value = True
        # Position
        set_position.inputs[2].default_value = (0.0, 0.0, 0.0)
        # Offset
        set_position.inputs[3].default_value = (0.0, 0.9999999403953552, 0.0)

        # Set locations
        group_output_2.location = (872.0143432617188, -10.004188537597656)
        group_input_2.location = (-787.0619506835938, -107.5450210571289)
        group_001.location = (-514.5983276367188, -28.69261932373047)
        instance_on_points.location = (-209.08261108398438, -105.87789154052734)
        curve_line.location = (-495.3824157714844, -235.96023559570312)
        points_1.location = (-135.04010009765625, 159.05178833007812)
        combine_xyz_1.location = (-299.6531066894531, 52.51677703857422)
        join_geometry_1.location = (637.0369262695312, -49.12348175048828)
        points_001.location = (-161.76303100585938, 303.4884948730469)
        combine_xyz_001_1.location = (-326.3760070800781, 196.95346069335938)
        points_to_curves.location = (210.1683349609375, 228.92160034179688)
        join_geometry_001.location = (38.02094268798828, 207.65298461914062)
        set_position.location = (400.6332702636719, 135.80914306640625)

        # Set dimensions
        group_output_2.width, group_output_2.height = 140.0, 100.0
        group_input_2.width, group_input_2.height = 140.0, 100.0
        group_001.width, group_001.height = 140.0, 100.0
        instance_on_points.width, instance_on_points.height = 140.0, 100.0
        curve_line.width, curve_line.height = 140.0, 100.0
        points_1.width, points_1.height = 140.0, 100.0
        combine_xyz_1.width, combine_xyz_1.height = 140.0, 100.0
        join_geometry_1.width, join_geometry_1.height = 140.0, 100.0
        points_001.width, points_001.height = 140.0, 100.0
        combine_xyz_001_1.width, combine_xyz_001_1.height = 140.0, 100.0
        points_to_curves.width, points_to_curves.height = 140.0, 100.0
        join_geometry_001.width, join_geometry_001.height = 140.0, 100.0
        set_position.width, set_position.height = 140.0, 100.0

        # Initialize ticks links

        # join_geometry_001.Geometry -> points_to_curves.Points
        ticks.links.new(join_geometry_001.outputs[0], points_to_curves.inputs[0])
        # points_to_curves.Curves -> set_position.Geometry
        ticks.links.new(points_to_curves.outputs[0], set_position.inputs[0])
        # instance_on_points.Instances -> join_geometry_1.Geometry
        ticks.links.new(instance_on_points.outputs[0], join_geometry_1.inputs[0])
        # combine_xyz_001_1.Vector -> points_001.Position
        ticks.links.new(combine_xyz_001_1.outputs[0], points_001.inputs[1])
        # points_1.Points -> join_geometry_001.Geometry
        ticks.links.new(points_1.outputs[0], join_geometry_001.inputs[0])
        # group_001.Xmin -> combine_xyz_001_1.X
        ticks.links.new(group_001.outputs[1], combine_xyz_001_1.inputs[0])
        # group_001.Xmax -> combine_xyz_1.X
        ticks.links.new(group_001.outputs[2], combine_xyz_1.inputs[0])
        # curve_line.Curve -> instance_on_points.Instance
        ticks.links.new(curve_line.outputs[0], instance_on_points.inputs[2])
        # combine_xyz_1.Vector -> points_1.Position
        ticks.links.new(combine_xyz_1.outputs[0], points_1.inputs[1])
        # group_001.Points -> instance_on_points.Points
        ticks.links.new(group_001.outputs[0], instance_on_points.inputs[0])
        # group_input_2.Size -> group_001.Size
        ticks.links.new(group_input_2.outputs[0], group_001.inputs[0])
        # group_input_2.Delta -> group_001.Delta
        ticks.links.new(group_input_2.outputs[1], group_001.inputs[1])
        # join_geometry_1.Geometry -> group_output_2.Geometry
        ticks.links.new(join_geometry_1.outputs[0], group_output_2.inputs[0])
        # set_position.Geometry -> join_geometry_1.Geometry
        ticks.links.new(set_position.outputs[0], join_geometry_1.inputs[0])
        # points_001.Points -> join_geometry_001.Geometry
        ticks.links.new(points_001.outputs[0], join_geometry_001.inputs[0])
        # points_to_curves.Curves -> join_geometry_1.Geometry
        ticks.links.new(points_to_curves.outputs[0], join_geometry_1.inputs[0])

        return ticks

    ticks = ticks_node_group()

    def transformation_node_group():
        """Initialize transformation node group"""
        transformation = bpy.data.node_groups.new(
            type="GeometryNodeTree", name="Transformation"
        )

        transformation.color_tag = "NONE"
        transformation.description = ""
        transformation.default_group_node_width = 140

        # transformation interface

        # Socket Translation
        translation_socket = transformation.interface.new_socket(
            name="Translation", in_out="OUTPUT", socket_type="NodeSocketVector"
        )
        translation_socket.default_value = (0.0, 0.0, 0.0)
        translation_socket.min_value = -3.4028234663852886e38
        translation_socket.max_value = 3.4028234663852886e38
        translation_socket.subtype = "NONE"
        translation_socket.attribute_domain = "POINT"
        translation_socket.default_input = "VALUE"

        # Socket Rotation
        rotation_socket = transformation.interface.new_socket(
            name="Rotation", in_out="OUTPUT", socket_type="NodeSocketRotation"
        )
        rotation_socket.default_value = (0.0, 0.0, 0.0)
        rotation_socket.attribute_domain = "POINT"
        rotation_socket.default_input = "VALUE"

        # Socket Stretch
        stretch_socket = transformation.interface.new_socket(
            name="Stretch", in_out="OUTPUT", socket_type="NodeSocketVector"
        )
        stretch_socket.default_value = (0.0, 0.0, 0.0)
        stretch_socket.min_value = -3.4028234663852886e38
        stretch_socket.max_value = 3.4028234663852886e38
        stretch_socket.subtype = "NONE"
        stretch_socket.attribute_domain = "POINT"
        stretch_socket.default_input = "VALUE"

        # Socket SizeAcross
        sizeacross_socket = transformation.interface.new_socket(
            name="SizeAcross", in_out="INPUT", socket_type="NodeSocketFloat"
        )
        sizeacross_socket.default_value = 1.0
        sizeacross_socket.min_value = -10000.0
        sizeacross_socket.max_value = 10000.0
        sizeacross_socket.subtype = "NONE"
        sizeacross_socket.attribute_domain = "POINT"
        sizeacross_socket.default_input = "VALUE"

        # Socket Sizes
        sizes_socket = transformation.interface.new_socket(
            name="Sizes", in_out="INPUT", socket_type="NodeSocketVector"
        )
        sizes_socket.default_value = (0.0, 0.0, 0.0)
        sizes_socket.min_value = -3.4028234663852886e38
        sizes_socket.max_value = 3.4028234663852886e38
        sizes_socket.subtype = "NONE"
        sizes_socket.attribute_domain = "POINT"
        sizes_socket.default_input = "VALUE"

        # Socket TranslateInXYZ
        translateinxyz_socket = transformation.interface.new_socket(
            name="TranslateInXYZ", in_out="INPUT", socket_type="NodeSocketVector"
        )
        translateinxyz_socket.default_value = (0.0, 0.0, 0.0)
        translateinxyz_socket.min_value = -3.4028234663852886e38
        translateinxyz_socket.max_value = 3.4028234663852886e38
        translateinxyz_socket.subtype = "NONE"
        translateinxyz_socket.attribute_domain = "POINT"
        translateinxyz_socket.default_input = "VALUE"

        # Socket RotateInXYZ
        rotateinxyz_socket = transformation.interface.new_socket(
            name="RotateInXYZ", in_out="INPUT", socket_type="NodeSocketVector"
        )
        rotateinxyz_socket.default_value = (0.0, 0.0, 0.0)
        rotateinxyz_socket.min_value = -3.4028234663852886e38
        rotateinxyz_socket.max_value = 3.4028234663852886e38
        rotateinxyz_socket.subtype = "NONE"
        rotateinxyz_socket.attribute_domain = "POINT"
        rotateinxyz_socket.default_input = "VALUE"

        # Initialize transformation nodes

        # Node Group Output
        group_output_3 = transformation.nodes.new("NodeGroupOutput")
        group_output_3.name = "Group Output"
        group_output_3.is_active_output = True

        # Node Group Input
        group_input_3 = transformation.nodes.new("NodeGroupInput")
        group_input_3.name = "Group Input"

        # Node Combine XYZ.002
        combine_xyz_002 = transformation.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_002.name = "Combine XYZ.002"
        # X
        combine_xyz_002.inputs[0].default_value = 1.0
        # Z
        combine_xyz_002.inputs[2].default_value = 1.0

        # Node Combine XYZ.003
        combine_xyz_003 = transformation.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_003.name = "Combine XYZ.003"

        # Node Math
        math_1 = transformation.nodes.new("ShaderNodeMath")
        math_1.name = "Math"
        math_1.operation = "MULTIPLY"
        math_1.use_clamp = False

        # Node Math.001
        math_001_1 = transformation.nodes.new("ShaderNodeMath")
        math_001_1.name = "Math.001"
        math_001_1.operation = "MULTIPLY"
        math_001_1.use_clamp = False

        # Node Math.002
        math_002_2 = transformation.nodes.new("ShaderNodeMath")
        math_002_2.name = "Math.002"
        math_002_2.operation = "MULTIPLY"
        math_002_2.use_clamp = False

        # Node Euler to Rotation
        euler_to_rotation = transformation.nodes.new("FunctionNodeEulerToRotation")
        euler_to_rotation.name = "Euler to Rotation"

        # Node Combine XYZ.004
        combine_xyz_004 = transformation.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_004.name = "Combine XYZ.004"

        # Node Math.003
        math_003_1 = transformation.nodes.new("ShaderNodeMath")
        math_003_1.name = "Math.003"
        math_003_1.operation = "MULTIPLY"
        math_003_1.use_clamp = False
        # Value_001
        math_003_1.inputs[1].default_value = 1.5707963705062866

        # Node Math.004
        math_004_1 = transformation.nodes.new("ShaderNodeMath")
        math_004_1.name = "Math.004"
        math_004_1.operation = "MULTIPLY"
        math_004_1.use_clamp = False
        # Value_001
        math_004_1.inputs[1].default_value = -1.5707999467849731

        # Node Math.005
        math_005 = transformation.nodes.new("ShaderNodeMath")
        math_005.name = "Math.005"
        math_005.operation = "MULTIPLY"
        math_005.use_clamp = False
        # Value_001
        math_005.inputs[1].default_value = 1.5707963705062866

        # Node Separate XYZ
        separate_xyz_1 = transformation.nodes.new("ShaderNodeSeparateXYZ")
        separate_xyz_1.name = "Separate XYZ"

        # Node Separate XYZ.001
        separate_xyz_001_1 = transformation.nodes.new("ShaderNodeSeparateXYZ")
        separate_xyz_001_1.name = "Separate XYZ.001"

        # Node Separate XYZ.002
        separate_xyz_002 = transformation.nodes.new("ShaderNodeSeparateXYZ")
        separate_xyz_002.name = "Separate XYZ.002"

        # Set locations
        group_output_3.location = (496.5140380859375, 87.73368072509766)
        group_input_3.location = (-1100.090087890625, 144.7731475830078)
        combine_xyz_002.location = (106.94705200195312, 204.04754638671875)
        combine_xyz_003.location = (45.0340576171875, 442.43450927734375)
        math_1.location = (-224.39898681640625, 423.380615234375)
        math_001_1.location = (-217.4063720703125, 253.99331665039062)
        math_002_2.location = (-223.56396484375, 82.05545043945312)
        euler_to_rotation.location = (133.8450927734375, -36.325469970703125)
        combine_xyz_004.location = (-37.03596496582031, -165.24514770507812)
        math_003_1.location = (-286.1660461425781, -114.84030151367188)
        math_004_1.location = (-282.2108459472656, -281.1115417480469)
        math_005.location = (-278.2556457519531, -442.4344787597656)
        separate_xyz_1.location = (-544.4893798828125, 464.2496337890625)
        separate_xyz_001_1.location = (-580.1639404296875, 288.45928955078125)
        separate_xyz_002.location = (-615.83837890625, -57.627891540527344)

        # Set dimensions
        group_output_3.width, group_output_3.height = 140.0, 100.0
        group_input_3.width, group_input_3.height = 140.0, 100.0
        combine_xyz_002.width, combine_xyz_002.height = 140.0, 100.0
        combine_xyz_003.width, combine_xyz_003.height = 140.0, 100.0
        math_1.width, math_1.height = 140.0, 100.0
        math_001_1.width, math_001_1.height = 140.0, 100.0
        math_002_2.width, math_002_2.height = 140.0, 100.0
        euler_to_rotation.width, euler_to_rotation.height = 140.0, 100.0
        combine_xyz_004.width, combine_xyz_004.height = 140.0, 100.0
        math_003_1.width, math_003_1.height = 140.0, 100.0
        math_004_1.width, math_004_1.height = 140.0, 100.0
        math_005.width, math_005.height = 140.0, 100.0
        separate_xyz_1.width, separate_xyz_1.height = 140.0, 100.0
        separate_xyz_001_1.width, separate_xyz_001_1.height = 140.0, 100.0
        separate_xyz_002.width, separate_xyz_002.height = 140.0, 100.0

        # Initialize transformation links

        # combine_xyz_004.Vector -> euler_to_rotation.Euler
        transformation.links.new(
            combine_xyz_004.outputs[0], euler_to_rotation.inputs[0]
        )
        # math_005.Value -> combine_xyz_004.Z
        transformation.links.new(math_005.outputs[0], combine_xyz_004.inputs[2])
        # math_002_2.Value -> combine_xyz_003.Z
        transformation.links.new(math_002_2.outputs[0], combine_xyz_003.inputs[2])
        # math_001_1.Value -> combine_xyz_003.Y
        transformation.links.new(math_001_1.outputs[0], combine_xyz_003.inputs[1])
        # math_003_1.Value -> combine_xyz_004.X
        transformation.links.new(math_003_1.outputs[0], combine_xyz_004.inputs[0])
        # math_1.Value -> combine_xyz_003.X
        transformation.links.new(math_1.outputs[0], combine_xyz_003.inputs[0])
        # math_004_1.Value -> combine_xyz_004.Y
        transformation.links.new(math_004_1.outputs[0], combine_xyz_004.inputs[1])
        # group_input_3.SizeAcross -> combine_xyz_002.Y
        transformation.links.new(group_input_3.outputs[0], combine_xyz_002.inputs[1])
        # combine_xyz_002.Vector -> group_output_3.Stretch
        transformation.links.new(combine_xyz_002.outputs[0], group_output_3.inputs[2])
        # combine_xyz_003.Vector -> group_output_3.Translation
        transformation.links.new(combine_xyz_003.outputs[0], group_output_3.inputs[0])
        # euler_to_rotation.Rotation -> group_output_3.Rotation
        transformation.links.new(euler_to_rotation.outputs[0], group_output_3.inputs[1])
        # group_input_3.Sizes -> separate_xyz_1.Vector
        transformation.links.new(group_input_3.outputs[1], separate_xyz_1.inputs[0])
        # separate_xyz_1.X -> math_1.Value
        transformation.links.new(separate_xyz_1.outputs[0], math_1.inputs[0])
        # separate_xyz_1.Y -> math_001_1.Value
        transformation.links.new(separate_xyz_1.outputs[1], math_001_1.inputs[0])
        # separate_xyz_1.Z -> math_002_2.Value
        transformation.links.new(separate_xyz_1.outputs[2], math_002_2.inputs[0])
        # group_input_3.TranslateInXYZ -> separate_xyz_001_1.Vector
        transformation.links.new(group_input_3.outputs[2], separate_xyz_001_1.inputs[0])
        # separate_xyz_001_1.X -> math_1.Value
        transformation.links.new(separate_xyz_001_1.outputs[0], math_1.inputs[1])
        # separate_xyz_001_1.Y -> math_001_1.Value
        transformation.links.new(separate_xyz_001_1.outputs[1], math_001_1.inputs[1])
        # separate_xyz_001_1.Z -> math_002_2.Value
        transformation.links.new(separate_xyz_001_1.outputs[2], math_002_2.inputs[1])
        # separate_xyz_002.X -> math_003_1.Value
        transformation.links.new(separate_xyz_002.outputs[0], math_003_1.inputs[0])
        # separate_xyz_002.Y -> math_004_1.Value
        transformation.links.new(separate_xyz_002.outputs[1], math_004_1.inputs[0])
        # separate_xyz_002.Z -> math_005.Value
        transformation.links.new(separate_xyz_002.outputs[2], math_005.inputs[0])
        # group_input_3.RotateInXYZ -> separate_xyz_002.Vector
        transformation.links.new(group_input_3.outputs[3], separate_xyz_002.inputs[0])

        return transformation

    transformation = transformation_node_group()

    def vectorcomponent_node_group():
        """Initialize vectorcomponent node group"""
        vectorcomponent = bpy.data.node_groups.new(
            type="GeometryNodeTree", name="VectorComponent"
        )

        vectorcomponent.color_tag = "NONE"
        vectorcomponent.description = ""
        vectorcomponent.default_group_node_width = 140

        # vectorcomponent interface

        # Socket Component
        component_socket = vectorcomponent.interface.new_socket(
            name="Component", in_out="OUTPUT", socket_type="NodeSocketFloat"
        )
        component_socket.default_value = 0.0
        component_socket.min_value = -3.4028234663852886e38
        component_socket.max_value = 3.4028234663852886e38
        component_socket.subtype = "NONE"
        component_socket.attribute_domain = "POINT"
        component_socket.default_input = "VALUE"

        # Socket Switch
        switch_socket = vectorcomponent.interface.new_socket(
            name="Switch", in_out="INPUT", socket_type="NodeSocketInt"
        )
        switch_socket.default_value = 0
        switch_socket.min_value = -2147483648
        switch_socket.max_value = 2147483647
        switch_socket.subtype = "NONE"
        switch_socket.attribute_domain = "POINT"
        switch_socket.default_input = "VALUE"

        # Socket Vector
        vector_socket = vectorcomponent.interface.new_socket(
            name="Vector", in_out="INPUT", socket_type="NodeSocketVector"
        )
        vector_socket.default_value = (0.0, 0.0, 0.0)
        vector_socket.min_value = -10000.0
        vector_socket.max_value = 10000.0
        vector_socket.subtype = "NONE"
        vector_socket.attribute_domain = "POINT"
        vector_socket.default_input = "VALUE"

        # Initialize vectorcomponent nodes

        # Node Group Output
        group_output_4 = vectorcomponent.nodes.new("NodeGroupOutput")
        group_output_4.name = "Group Output"
        group_output_4.is_active_output = True

        # Node Group Input
        group_input_4 = vectorcomponent.nodes.new("NodeGroupInput")
        group_input_4.name = "Group Input"

        # Node Compare
        compare_1 = vectorcomponent.nodes.new("FunctionNodeCompare")
        compare_1.name = "Compare"
        compare_1.data_type = "INT"
        compare_1.mode = "ELEMENT"
        compare_1.operation = "EQUAL"
        # B_INT
        compare_1.inputs[3].default_value = 0

        # Node Compare.001
        compare_001 = vectorcomponent.nodes.new("FunctionNodeCompare")
        compare_001.name = "Compare.001"
        compare_001.data_type = "INT"
        compare_001.mode = "ELEMENT"
        compare_001.operation = "EQUAL"
        # B_INT
        compare_001.inputs[3].default_value = 1

        # Node Separate XYZ.002
        separate_xyz_002_1 = vectorcomponent.nodes.new("ShaderNodeSeparateXYZ")
        separate_xyz_002_1.name = "Separate XYZ.002"

        # Node Switch
        switch_1 = vectorcomponent.nodes.new("GeometryNodeSwitch")
        switch_1.name = "Switch"
        switch_1.input_type = "FLOAT"

        # Node Switch.001
        switch_001 = vectorcomponent.nodes.new("GeometryNodeSwitch")
        switch_001.name = "Switch.001"
        switch_001.input_type = "FLOAT"

        # Set locations
        group_output_4.location = (609.3634643554688, 0.0)
        group_input_4.location = (-734.4200439453125, 14.8849515914917)
        compare_1.location = (-419.36346435546875, 111.7698974609375)
        compare_001.location = (-413.87518310546875, -51.1982421875)
        separate_xyz_002_1.location = (-82.7672119140625, -111.7698974609375)
        switch_1.location = (419.36346435546875, 101.59820556640625)
        switch_001.location = (166.9027099609375, -35.7349853515625)

        # Set dimensions
        group_output_4.width, group_output_4.height = 140.0, 100.0
        group_input_4.width, group_input_4.height = 140.0, 100.0
        compare_1.width, compare_1.height = 140.0, 100.0
        compare_001.width, compare_001.height = 140.0, 100.0
        separate_xyz_002_1.width, separate_xyz_002_1.height = 140.0, 100.0
        switch_1.width, switch_1.height = 140.0, 100.0
        switch_001.width, switch_001.height = 140.0, 100.0

        # Initialize vectorcomponent links

        # compare_001.Result -> switch_001.Switch
        vectorcomponent.links.new(compare_001.outputs[0], switch_001.inputs[0])
        # compare_1.Result -> switch_1.Switch
        vectorcomponent.links.new(compare_1.outputs[0], switch_1.inputs[0])
        # separate_xyz_002_1.Y -> switch_001.True
        vectorcomponent.links.new(separate_xyz_002_1.outputs[1], switch_001.inputs[2])
        # separate_xyz_002_1.Z -> switch_001.False
        vectorcomponent.links.new(separate_xyz_002_1.outputs[2], switch_001.inputs[1])
        # switch_001.Output -> switch_1.False
        vectorcomponent.links.new(switch_001.outputs[0], switch_1.inputs[1])
        # separate_xyz_002_1.X -> switch_1.True
        vectorcomponent.links.new(separate_xyz_002_1.outputs[0], switch_1.inputs[2])
        # group_input_4.Switch -> compare_1.A
        vectorcomponent.links.new(group_input_4.outputs[0], compare_1.inputs[2])
        # group_input_4.Vector -> separate_xyz_002_1.Vector
        vectorcomponent.links.new(
            group_input_4.outputs[1], separate_xyz_002_1.inputs[0]
        )
        # switch_1.Output -> group_output_4.Component
        vectorcomponent.links.new(switch_1.outputs[0], group_output_4.inputs[0])
        # group_input_4.Switch -> compare_001.A
        vectorcomponent.links.new(group_input_4.outputs[0], compare_001.inputs[2])

        return vectorcomponent

    vectorcomponent = vectorcomponent_node_group()

    def oneside_node_group():
        """Initialize oneside node group"""
        oneside = bpy.data.node_groups.new(type="GeometryNodeTree", name="OneSide")

        oneside.color_tag = "NONE"
        oneside.description = ""
        oneside.default_group_node_width = 140

        # oneside interface

        # Socket Mesh
        mesh_socket = oneside.interface.new_socket(
            name="Mesh", in_out="OUTPUT", socket_type="NodeSocketGeometry"
        )
        mesh_socket.attribute_domain = "POINT"
        mesh_socket.default_input = "VALUE"

        # Socket Sizes
        sizes_socket_1 = oneside.interface.new_socket(
            name="Sizes", in_out="INPUT", socket_type="NodeSocketVector"
        )
        sizes_socket_1.default_value = (0.0, 0.0, 0.0)
        sizes_socket_1.min_value = -3.4028234663852886e38
        sizes_socket_1.max_value = 3.4028234663852886e38
        sizes_socket_1.subtype = "NONE"
        sizes_socket_1.attribute_domain = "POINT"
        sizes_socket_1.default_input = "VALUE"

        # Socket Deltas
        deltas_socket = oneside.interface.new_socket(
            name="Deltas", in_out="INPUT", socket_type="NodeSocketVector"
        )
        deltas_socket.default_value = (0.0, 0.0, 0.0)
        deltas_socket.min_value = -3.4028234663852886e38
        deltas_socket.max_value = 3.4028234663852886e38
        deltas_socket.subtype = "NONE"
        deltas_socket.attribute_domain = "POINT"
        deltas_socket.default_input = "VALUE"

        # Socket SideAlong
        sidealong_socket = oneside.interface.new_socket(
            name="SideAlong", in_out="INPUT", socket_type="NodeSocketInt"
        )
        sidealong_socket.default_value = 0
        sidealong_socket.min_value = 0
        sidealong_socket.max_value = 2
        sidealong_socket.subtype = "NONE"
        sidealong_socket.attribute_domain = "POINT"
        sidealong_socket.default_input = "VALUE"

        # Socket SideAcross
        sideacross_socket = oneside.interface.new_socket(
            name="SideAcross", in_out="INPUT", socket_type="NodeSocketInt"
        )
        sideacross_socket.default_value = 0
        sideacross_socket.min_value = 0
        sideacross_socket.max_value = 2
        sideacross_socket.subtype = "NONE"
        sideacross_socket.attribute_domain = "POINT"
        sideacross_socket.default_input = "VALUE"

        # Socket TranslateInX
        translateinx_socket = oneside.interface.new_socket(
            name="TranslateInX", in_out="INPUT", socket_type="NodeSocketBool"
        )
        translateinx_socket.default_value = False
        translateinx_socket.attribute_domain = "POINT"
        translateinx_socket.default_input = "VALUE"

        # Socket TranslateInY
        translateiny_socket = oneside.interface.new_socket(
            name="TranslateInY", in_out="INPUT", socket_type="NodeSocketBool"
        )
        translateiny_socket.default_value = False
        translateiny_socket.attribute_domain = "POINT"
        translateiny_socket.default_input = "VALUE"

        # Socket TranslateInZ
        translateinz_socket = oneside.interface.new_socket(
            name="TranslateInZ", in_out="INPUT", socket_type="NodeSocketBool"
        )
        translateinz_socket.default_value = False
        translateinz_socket.attribute_domain = "POINT"
        translateinz_socket.default_input = "VALUE"

        # Socket RotateInX
        rotateinx_socket = oneside.interface.new_socket(
            name="RotateInX", in_out="INPUT", socket_type="NodeSocketBool"
        )
        rotateinx_socket.default_value = False
        rotateinx_socket.attribute_domain = "POINT"
        rotateinx_socket.default_input = "VALUE"

        # Socket RotateInY
        rotateiny_socket = oneside.interface.new_socket(
            name="RotateInY", in_out="INPUT", socket_type="NodeSocketBool"
        )
        rotateiny_socket.default_value = False
        rotateiny_socket.attribute_domain = "POINT"
        rotateiny_socket.default_input = "VALUE"

        # Socket RotateInZ
        rotateinz_socket = oneside.interface.new_socket(
            name="RotateInZ", in_out="INPUT", socket_type="NodeSocketBool"
        )
        rotateinz_socket.default_value = False
        rotateinz_socket.attribute_domain = "POINT"
        rotateinz_socket.default_input = "VALUE"

        # Initialize oneside nodes

        # Node Group Output
        group_output_5 = oneside.nodes.new("NodeGroupOutput")
        group_output_5.name = "Group Output"
        group_output_5.is_active_output = True

        # Node Group Input
        group_input_5 = oneside.nodes.new("NodeGroupInput")
        group_input_5.name = "Group Input"

        # Node Transform Geometry
        transform_geometry = oneside.nodes.new("GeometryNodeTransform")
        transform_geometry.name = "Transform Geometry"
        transform_geometry.mode = "COMPONENTS"

        # Node Group
        group_1 = oneside.nodes.new("GeometryNodeGroup")
        group_1.name = "Group"
        group_1.node_tree = ticks

        # Node Group.001
        group_001_1 = oneside.nodes.new("GeometryNodeGroup")
        group_001_1.name = "Group.001"
        group_001_1.node_tree = transformation

        # Node Group.002
        group_002 = oneside.nodes.new("GeometryNodeGroup")
        group_002.name = "Group.002"
        group_002.node_tree = ticks

        # Node Transform Geometry.001
        transform_geometry_001 = oneside.nodes.new("GeometryNodeTransform")
        transform_geometry_001.name = "Transform Geometry.001"
        transform_geometry_001.mode = "COMPONENTS"
        # Scale
        transform_geometry_001.inputs[3].default_value = (1.0, 1.0, 1.0)

        # Node Group.003
        group_003 = oneside.nodes.new("GeometryNodeGroup")
        group_003.name = "Group.003"
        group_003.node_tree = transformation

        # Node Join Geometry
        join_geometry_2 = oneside.nodes.new("GeometryNodeJoinGeometry")
        join_geometry_2.name = "Join Geometry"

        # Node Combine XYZ
        combine_xyz_2 = oneside.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_2.name = "Combine XYZ"
        # Y
        combine_xyz_2.inputs[1].default_value = 0.0
        # Z
        combine_xyz_2.inputs[2].default_value = 0.0

        # Node Group.004
        group_004 = oneside.nodes.new("GeometryNodeGroup")
        group_004.name = "Group.004"
        group_004.node_tree = vectorcomponent

        # Node Group.005
        group_005 = oneside.nodes.new("GeometryNodeGroup")
        group_005.name = "Group.005"
        group_005.node_tree = vectorcomponent

        # Node Group.006
        group_006 = oneside.nodes.new("GeometryNodeGroup")
        group_006.name = "Group.006"
        group_006.node_tree = vectorcomponent

        # Node Group.007
        group_007 = oneside.nodes.new("GeometryNodeGroup")
        group_007.name = "Group.007"
        group_007.node_tree = vectorcomponent

        # Node Combine XYZ.001
        combine_xyz_001_2 = oneside.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_001_2.name = "Combine XYZ.001"

        # Node Combine XYZ.002
        combine_xyz_002_1 = oneside.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_002_1.name = "Combine XYZ.002"

        # Node Transform Geometry.002
        transform_geometry_002 = oneside.nodes.new("GeometryNodeTransform")
        transform_geometry_002.name = "Transform Geometry.002"
        transform_geometry_002.mode = "COMPONENTS"
        # Rotation
        transform_geometry_002.inputs[2].default_value = (0.0, 0.0, 1.5707963705062866)

        # Set locations
        group_output_5.location = (15.189788818359375, 112.72354125976562)
        group_input_5.location = (-1942.9461669921875, 148.48095703125)
        transform_geometry.location = (-695.24609375, 312.37933349609375)
        group_1.location = (-1063.3341064453125, 375.34320068359375)
        group_001_1.location = (-1068.02734375, 247.99850463867188)
        group_002.location = (-1070.2681884765625, -118.5830078125)
        transform_geometry_001.location = (-527.4822998046875, -7.790733337402344)
        group_003.location = (-1071.494384765625, -279.4732971191406)
        join_geometry_2.location = (-298.9493408203125, 125.973876953125)
        combine_xyz_2.location = (-1014.797119140625, 22.935256958007812)
        group_004.location = (-1333.4810791015625, 297.64306640625)
        group_005.location = (-1338.0546875, 170.37921142578125)
        group_006.location = (-1344.039794921875, 37.9913330078125)
        group_007.location = (-1341.2955322265625, -98.42819213867188)
        combine_xyz_001_2.location = (-1633.977783203125, -38.750606536865234)
        combine_xyz_002_1.location = (-1630.022216796875, -172.3756103515625)
        transform_geometry_002.location = (-762.7105712890625, 71.82022094726562)

        # Set dimensions
        group_output_5.width, group_output_5.height = 140.0, 100.0
        group_input_5.width, group_input_5.height = 140.0, 100.0
        transform_geometry.width, transform_geometry.height = 140.0, 100.0
        group_1.width, group_1.height = 140.0, 100.0
        group_001_1.width, group_001_1.height = 140.0, 100.0
        group_002.width, group_002.height = 140.0, 100.0
        transform_geometry_001.width, transform_geometry_001.height = 140.0, 100.0
        group_003.width, group_003.height = 140.0, 100.0
        join_geometry_2.width, join_geometry_2.height = 140.0, 100.0
        combine_xyz_2.width, combine_xyz_2.height = 140.0, 100.0
        group_004.width, group_004.height = 140.0, 100.0
        group_005.width, group_005.height = 140.0, 100.0
        group_006.width, group_006.height = 140.0, 100.0
        group_007.width, group_007.height = 140.0, 100.0
        combine_xyz_001_2.width, combine_xyz_001_2.height = 140.0, 100.0
        combine_xyz_002_1.width, combine_xyz_002_1.height = 140.0, 100.0
        transform_geometry_002.width, transform_geometry_002.height = 140.0, 100.0

        # Initialize oneside links

        # group_1.Geometry -> transform_geometry.Geometry
        oneside.links.new(group_1.outputs[0], transform_geometry.inputs[0])
        # group_001_1.Stretch -> transform_geometry.Scale
        oneside.links.new(group_001_1.outputs[2], transform_geometry.inputs[3])
        # group_001_1.Translation -> transform_geometry.Translation
        oneside.links.new(group_001_1.outputs[0], transform_geometry.inputs[1])
        # join_geometry_2.Geometry -> group_output_5.Mesh
        oneside.links.new(join_geometry_2.outputs[0], group_output_5.inputs[0])
        # group_001_1.Rotation -> transform_geometry.Rotation
        oneside.links.new(group_001_1.outputs[1], transform_geometry.inputs[2])
        # transform_geometry_002.Geometry -> transform_geometry_001.Geometry
        oneside.links.new(
            transform_geometry_002.outputs[0], transform_geometry_001.inputs[0]
        )
        # group_003.Rotation -> transform_geometry_001.Rotation
        oneside.links.new(group_003.outputs[1], transform_geometry_001.inputs[2])
        # transform_geometry_001.Geometry -> join_geometry_2.Geometry
        oneside.links.new(transform_geometry_001.outputs[0], join_geometry_2.inputs[0])
        # combine_xyz_001_2.Vector -> group_003.TranslateInXYZ
        oneside.links.new(combine_xyz_001_2.outputs[0], group_003.inputs[2])
        # group_003.Translation -> transform_geometry_001.Translation
        oneside.links.new(group_003.outputs[0], transform_geometry_001.inputs[1])
        # group_input_5.SideAlong -> group_004.Switch
        oneside.links.new(group_input_5.outputs[2], group_004.inputs[0])
        # group_input_5.Sizes -> group_004.Vector
        oneside.links.new(group_input_5.outputs[0], group_004.inputs[1])
        # group_input_5.Sizes -> group_001_1.Sizes
        oneside.links.new(group_input_5.outputs[0], group_001_1.inputs[1])
        # group_input_5.Deltas -> group_005.Vector
        oneside.links.new(group_input_5.outputs[1], group_005.inputs[1])
        # group_input_5.SideAlong -> group_005.Switch
        oneside.links.new(group_input_5.outputs[2], group_005.inputs[0])
        # group_004.Component -> group_1.Size
        oneside.links.new(group_004.outputs[0], group_1.inputs[0])
        # group_005.Component -> group_1.Delta
        oneside.links.new(group_005.outputs[0], group_1.inputs[1])
        # group_input_5.SideAcross -> group_006.Switch
        oneside.links.new(group_input_5.outputs[3], group_006.inputs[0])
        # group_input_5.Sizes -> group_006.Vector
        oneside.links.new(group_input_5.outputs[0], group_006.inputs[1])
        # group_006.Component -> group_001_1.SizeAcross
        oneside.links.new(group_006.outputs[0], group_001_1.inputs[0])
        # group_input_5.SideAcross -> group_007.Switch
        oneside.links.new(group_input_5.outputs[3], group_007.inputs[0])
        # group_input_5.Deltas -> group_007.Vector
        oneside.links.new(group_input_5.outputs[1], group_007.inputs[1])
        # group_007.Component -> group_002.Delta
        oneside.links.new(group_007.outputs[0], group_002.inputs[1])
        # group_006.Component -> group_002.Size
        oneside.links.new(group_006.outputs[0], group_002.inputs[0])
        # group_004.Component -> group_003.SizeAcross
        oneside.links.new(group_004.outputs[0], group_003.inputs[0])
        # group_input_5.Sizes -> group_003.Sizes
        oneside.links.new(group_input_5.outputs[0], group_003.inputs[1])
        # group_input_5.TranslateInX -> combine_xyz_001_2.X
        oneside.links.new(group_input_5.outputs[4], combine_xyz_001_2.inputs[0])
        # group_input_5.TranslateInY -> combine_xyz_001_2.Y
        oneside.links.new(group_input_5.outputs[5], combine_xyz_001_2.inputs[1])
        # group_input_5.TranslateInZ -> combine_xyz_001_2.Z
        oneside.links.new(group_input_5.outputs[6], combine_xyz_001_2.inputs[2])
        # group_input_5.RotateInX -> combine_xyz_002_1.X
        oneside.links.new(group_input_5.outputs[7], combine_xyz_002_1.inputs[0])
        # group_input_5.RotateInY -> combine_xyz_002_1.Y
        oneside.links.new(group_input_5.outputs[8], combine_xyz_002_1.inputs[1])
        # group_input_5.RotateInZ -> combine_xyz_002_1.Z
        oneside.links.new(group_input_5.outputs[9], combine_xyz_002_1.inputs[2])
        # combine_xyz_002_1.Vector -> group_003.RotateInXYZ
        oneside.links.new(combine_xyz_002_1.outputs[0], group_003.inputs[3])
        # combine_xyz_001_2.Vector -> group_001_1.TranslateInXYZ
        oneside.links.new(combine_xyz_001_2.outputs[0], group_001_1.inputs[2])
        # combine_xyz_002_1.Vector -> group_001_1.RotateInXYZ
        oneside.links.new(combine_xyz_002_1.outputs[0], group_001_1.inputs[3])
        # group_004.Component -> combine_xyz_2.X
        oneside.links.new(group_004.outputs[0], combine_xyz_2.inputs[0])
        # group_002.Geometry -> transform_geometry_002.Geometry
        oneside.links.new(group_002.outputs[0], transform_geometry_002.inputs[0])
        # group_003.Stretch -> transform_geometry_002.Scale
        oneside.links.new(group_003.outputs[2], transform_geometry_002.inputs[3])
        # combine_xyz_2.Vector -> transform_geometry_002.Translation
        oneside.links.new(combine_xyz_2.outputs[0], transform_geometry_002.inputs[1])
        # transform_geometry.Geometry -> join_geometry_2.Geometry
        oneside.links.new(transform_geometry.outputs[0], join_geometry_2.inputs[0])

        return oneside

    oneside = oneside_node_group()

    def outline_node_group():
        """Initialize outline node group"""
        outline = bpy.data.node_groups.new(type="GeometryNodeTree", name="Outline")

        outline.color_tag = "NONE"
        outline.description = ""
        outline.default_group_node_width = 140

        # outline interface

        # Socket Mesh
        mesh_socket_1 = outline.interface.new_socket(
            name="Mesh", in_out="OUTPUT", socket_type="NodeSocketGeometry"
        )
        mesh_socket_1.attribute_domain = "POINT"
        mesh_socket_1.default_input = "VALUE"

        # Socket Curve
        curve_socket = outline.interface.new_socket(
            name="Curve", in_out="INPUT", socket_type="NodeSocketGeometry"
        )
        curve_socket.attribute_domain = "POINT"
        curve_socket.default_input = "VALUE"

        # Socket Resolution
        resolution_socket = outline.interface.new_socket(
            name="Resolution", in_out="INPUT", socket_type="NodeSocketInt"
        )
        resolution_socket.default_value = 32
        resolution_socket.min_value = 3
        resolution_socket.max_value = 512
        resolution_socket.subtype = "NONE"
        resolution_socket.attribute_domain = "POINT"
        resolution_socket.description = "Number of points on the circle"
        resolution_socket.default_input = "VALUE"

        # Socket Radius
        radius_socket = outline.interface.new_socket(
            name="Radius", in_out="INPUT", socket_type="NodeSocketFloat"
        )
        radius_socket.default_value = 1.0
        radius_socket.min_value = 0.0
        radius_socket.max_value = 3.4028234663852886e38
        radius_socket.subtype = "DISTANCE"
        radius_socket.attribute_domain = "POINT"
        radius_socket.description = "Distance of the points from the origin"
        radius_socket.default_input = "VALUE"

        # Initialize outline nodes

        # Node Group Output
        group_output_6 = outline.nodes.new("NodeGroupOutput")
        group_output_6.name = "Group Output"
        group_output_6.is_active_output = True

        # Node Group Input
        group_input_6 = outline.nodes.new("NodeGroupInput")
        group_input_6.name = "Group Input"

        # Node Curve to Mesh
        curve_to_mesh = outline.nodes.new("GeometryNodeCurveToMesh")
        curve_to_mesh.name = "Curve to Mesh"
        if bpy.app.version >= (4, 5, 0):
            # Scale
            curve_to_mesh.inputs[2].default_value = 1.0
            # Fill Caps
            curve_to_mesh.inputs[3].default_value = False
        else:
            # Fill Caps
            curve_to_mesh.inputs[2].default_value = False

        # Node Mesh to Curve
        mesh_to_curve = outline.nodes.new("GeometryNodeMeshToCurve")
        mesh_to_curve.name = "Mesh to Curve"
        # Selection
        mesh_to_curve.inputs[1].default_value = True

        # Node Curve to Mesh.001
        curve_to_mesh_001 = outline.nodes.new("GeometryNodeCurveToMesh")
        curve_to_mesh_001.name = "Curve to Mesh.001"
        if bpy.app.version >= (4, 5, 0):
            # Scale
            curve_to_mesh_001.inputs[2].default_value = 1.0
            # Fill Caps
            curve_to_mesh_001.inputs[3].default_value = True
        else:
            # Fill Caps
            curve_to_mesh_001.inputs[2].default_value = True

        # Node Curve Circle
        curve_circle = outline.nodes.new("GeometryNodeCurvePrimitiveCircle")
        curve_circle.name = "Curve Circle"
        curve_circle.mode = "RADIUS"

        # Node Mesh Boolean
        mesh_boolean = outline.nodes.new("GeometryNodeMeshBoolean")
        mesh_boolean.name = "Mesh Boolean"
        mesh_boolean.operation = "UNION"
        mesh_boolean.solver = "FLOAT"

        # Set locations
        group_output_6.location = (455.8580627441406, 73.64271545410156)
        group_input_6.location = (-524.5691528320312, 0.0)
        curve_to_mesh.location = (-314.3938903808594, 120.33489227294922)
        mesh_to_curve.location = (50.255653381347656, 126.1717300415039)
        curve_to_mesh_001.location = (245.50759887695312, 103.31995391845703)
        curve_circle.location = (-65.96851348876953, -85.08040618896484)
        mesh_boolean.location = (-126.46525573730469, 108.60453796386719)

        # Set dimensions
        group_output_6.width, group_output_6.height = 140.0, 100.0
        group_input_6.width, group_input_6.height = 140.0, 100.0
        curve_to_mesh.width, curve_to_mesh.height = 140.0, 100.0
        mesh_to_curve.width, mesh_to_curve.height = 140.0, 100.0
        curve_to_mesh_001.width, curve_to_mesh_001.height = 140.0, 100.0
        curve_circle.width, curve_circle.height = 140.0, 100.0
        mesh_boolean.width, mesh_boolean.height = 140.0, 100.0

        # Initialize outline links

        # mesh_to_curve.Curve -> curve_to_mesh_001.Curve
        outline.links.new(mesh_to_curve.outputs[0], curve_to_mesh_001.inputs[0])
        # curve_circle.Curve -> curve_to_mesh_001.Profile Curve
        outline.links.new(curve_circle.outputs[0], curve_to_mesh_001.inputs[1])
        # group_input_6.Curve -> curve_to_mesh.Curve
        outline.links.new(group_input_6.outputs[0], curve_to_mesh.inputs[0])
        # group_input_6.Radius -> curve_circle.Radius
        outline.links.new(group_input_6.outputs[2], curve_circle.inputs[4])
        # group_input_6.Resolution -> curve_circle.Resolution
        outline.links.new(group_input_6.outputs[1], curve_circle.inputs[0])
        # curve_to_mesh_001.Mesh -> group_output_6.Mesh
        outline.links.new(curve_to_mesh_001.outputs[0], group_output_6.inputs[0])
        # curve_to_mesh.Mesh -> mesh_boolean.Mesh
        outline.links.new(curve_to_mesh.outputs[0], mesh_boolean.inputs[1])
        # mesh_boolean.Mesh -> mesh_to_curve.Mesh
        outline.links.new(mesh_boolean.outputs[0], mesh_to_curve.inputs[0])

        return outline

    outline = outline_node_group()

    def geometry_nodes_node_group():
        """Initialize geometry_nodes node group"""
        geometry_nodes = bpy.data.node_groups.new(
            type="GeometryNodeTree", name="Geometry Nodes"
        )

        geometry_nodes.color_tag = "NONE"
        geometry_nodes.description = ""
        geometry_nodes.default_group_node_width = 140
        geometry_nodes.is_modifier = True

        # geometry_nodes interface

        # Socket Geometry
        geometry_socket_1 = geometry_nodes.interface.new_socket(
            name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry"
        )
        geometry_socket_1.attribute_domain = "POINT"
        geometry_socket_1.default_input = "VALUE"

        # Socket Sizes
        sizes_socket_2 = geometry_nodes.interface.new_socket(
            name="Sizes", in_out="INPUT", socket_type="NodeSocketVector"
        )
        sizes_socket_2.default_value = (1.0, 1.0, 1.0)
        sizes_socket_2.min_value = 0.0
        sizes_socket_2.max_value = 3.402820018375656e38
        sizes_socket_2.subtype = "XYZ"
        sizes_socket_2.attribute_domain = "POINT"
        sizes_socket_2.default_input = "VALUE"

        # Socket Deltas
        deltas_socket_1 = geometry_nodes.interface.new_socket(
            name="Deltas", in_out="INPUT", socket_type="NodeSocketVector"
        )
        deltas_socket_1.default_value = (
            0.10000000149011612,
            0.10000000149011612,
            0.10000000149011612,
        )
        deltas_socket_1.min_value = 0.0
        deltas_socket_1.max_value = 3.402820018375656e38
        deltas_socket_1.subtype = "XYZ"
        deltas_socket_1.attribute_domain = "POINT"
        deltas_socket_1.default_input = "VALUE"

        # Socket +X
        _x_socket = geometry_nodes.interface.new_socket(
            name="+X", in_out="INPUT", socket_type="NodeSocketBool"
        )
        _x_socket.default_value = False
        _x_socket.attribute_domain = "POINT"
        _x_socket.default_input = "VALUE"

        # Socket -X
        _x_socket_1 = geometry_nodes.interface.new_socket(
            name="-X", in_out="INPUT", socket_type="NodeSocketBool"
        )
        _x_socket_1.default_value = True
        _x_socket_1.attribute_domain = "POINT"
        _x_socket_1.default_input = "VALUE"

        # Socket +Y
        _y_socket = geometry_nodes.interface.new_socket(
            name="+Y", in_out="INPUT", socket_type="NodeSocketBool"
        )
        _y_socket.default_value = False
        _y_socket.attribute_domain = "POINT"
        _y_socket.default_input = "VALUE"

        # Socket -Y
        _y_socket_1 = geometry_nodes.interface.new_socket(
            name="-Y", in_out="INPUT", socket_type="NodeSocketBool"
        )
        _y_socket_1.default_value = True
        _y_socket_1.attribute_domain = "POINT"
        _y_socket_1.default_input = "VALUE"

        # Socket +Z
        _z_socket = geometry_nodes.interface.new_socket(
            name="+Z", in_out="INPUT", socket_type="NodeSocketBool"
        )
        _z_socket.default_value = False
        _z_socket.attribute_domain = "POINT"
        _z_socket.default_input = "VALUE"

        # Socket -Z
        _z_socket_1 = geometry_nodes.interface.new_socket(
            name="-Z", in_out="INPUT", socket_type="NodeSocketBool"
        )
        _z_socket_1.default_value = True
        _z_socket_1.attribute_domain = "POINT"
        _z_socket_1.default_input = "VALUE"

        # Socket Resolution
        resolution_socket_1 = geometry_nodes.interface.new_socket(
            name="Resolution", in_out="INPUT", socket_type="NodeSocketInt"
        )
        resolution_socket_1.default_value = 32
        resolution_socket_1.min_value = 3
        resolution_socket_1.max_value = 512
        resolution_socket_1.subtype = "NONE"
        resolution_socket_1.attribute_domain = "POINT"
        resolution_socket_1.description = "Number of points on the circle"
        resolution_socket_1.default_input = "VALUE"

        # Socket Radius
        radius_socket_1 = geometry_nodes.interface.new_socket(
            name="Radius", in_out="INPUT", socket_type="NodeSocketFloat"
        )
        radius_socket_1.default_value = 0.0010000000474974513
        radius_socket_1.min_value = 0.0
        radius_socket_1.max_value = 3.4028234663852886e38
        radius_socket_1.subtype = "DISTANCE"
        radius_socket_1.attribute_domain = "POINT"
        radius_socket_1.description = "Distance of the points from the origin"
        radius_socket_1.default_input = "VALUE"

        # Initialize geometry_nodes nodes

        # Node Group Output
        group_output_7 = geometry_nodes.nodes.new("NodeGroupOutput")
        group_output_7.name = "Group Output"
        group_output_7.is_active_output = True

        # Node Group Input
        group_input_7 = geometry_nodes.nodes.new("NodeGroupInput")
        group_input_7.name = "Group Input"

        # Node Group
        group_2 = geometry_nodes.nodes.new("GeometryNodeGroup")
        group_2.label = "-Z"
        group_2.name = "Group"
        group_2.hide = True
        group_2.node_tree = oneside
        # Socket_17
        group_2.inputs[2].default_value = 0
        # Socket_3
        group_2.inputs[3].default_value = 1
        # Socket_9
        group_2.inputs[4].default_value = False
        # Socket_10
        group_2.inputs[5].default_value = False
        # Socket_11
        group_2.inputs[6].default_value = False
        # Socket_12
        group_2.inputs[7].default_value = False
        # Socket_13
        group_2.inputs[8].default_value = False
        # Socket_14
        group_2.inputs[9].default_value = False

        # Node Join Geometry
        join_geometry_3 = geometry_nodes.nodes.new("GeometryNodeJoinGeometry")
        join_geometry_3.name = "Join Geometry"

        # Node Group.001
        group_001_2 = geometry_nodes.nodes.new("GeometryNodeGroup")
        group_001_2.label = "+Z"
        group_001_2.name = "Group.001"
        group_001_2.hide = True
        group_001_2.node_tree = oneside
        # Socket_17
        group_001_2.inputs[2].default_value = 0
        # Socket_3
        group_001_2.inputs[3].default_value = 1
        # Socket_9
        group_001_2.inputs[4].default_value = False
        # Socket_10
        group_001_2.inputs[5].default_value = False
        # Socket_11
        group_001_2.inputs[6].default_value = True
        # Socket_12
        group_001_2.inputs[7].default_value = False
        # Socket_13
        group_001_2.inputs[8].default_value = False
        # Socket_14
        group_001_2.inputs[9].default_value = False

        # Node Group.002
        group_002_1 = geometry_nodes.nodes.new("GeometryNodeGroup")
        group_002_1.label = "-Y"
        group_002_1.name = "Group.002"
        group_002_1.hide = True
        group_002_1.node_tree = oneside
        # Socket_17
        group_002_1.inputs[2].default_value = 0
        # Socket_3
        group_002_1.inputs[3].default_value = 2
        # Socket_9
        group_002_1.inputs[4].default_value = False
        # Socket_10
        group_002_1.inputs[5].default_value = False
        # Socket_11
        group_002_1.inputs[6].default_value = False
        # Socket_12
        group_002_1.inputs[7].default_value = True
        # Socket_13
        group_002_1.inputs[8].default_value = False
        # Socket_14
        group_002_1.inputs[9].default_value = False

        # Node Group.003
        group_003_1 = geometry_nodes.nodes.new("GeometryNodeGroup")
        group_003_1.label = "+Y"
        group_003_1.name = "Group.003"
        group_003_1.hide = True
        group_003_1.node_tree = oneside
        # Socket_17
        group_003_1.inputs[2].default_value = 0
        # Socket_3
        group_003_1.inputs[3].default_value = 2
        # Socket_9
        group_003_1.inputs[4].default_value = False
        # Socket_10
        group_003_1.inputs[5].default_value = True
        # Socket_11
        group_003_1.inputs[6].default_value = False
        # Socket_12
        group_003_1.inputs[7].default_value = True
        # Socket_13
        group_003_1.inputs[8].default_value = False
        # Socket_14
        group_003_1.inputs[9].default_value = False

        # Node Group.004
        group_004_1 = geometry_nodes.nodes.new("GeometryNodeGroup")
        group_004_1.label = "-X"
        group_004_1.name = "Group.004"
        group_004_1.hide = True
        group_004_1.node_tree = oneside
        # Socket_17
        group_004_1.inputs[2].default_value = 1
        # Socket_3
        group_004_1.inputs[3].default_value = 2
        # Socket_9
        group_004_1.inputs[4].default_value = False
        # Socket_10
        group_004_1.inputs[5].default_value = False
        # Socket_11
        group_004_1.inputs[6].default_value = False
        # Socket_12
        group_004_1.inputs[7].default_value = True
        # Socket_13
        group_004_1.inputs[8].default_value = False
        # Socket_14
        group_004_1.inputs[9].default_value = True

        # Node Group.005
        group_005_1 = geometry_nodes.nodes.new("GeometryNodeGroup")
        group_005_1.label = "+X"
        group_005_1.name = "Group.005"
        group_005_1.hide = True
        group_005_1.node_tree = oneside
        # Socket_17
        group_005_1.inputs[2].default_value = 1
        # Socket_3
        group_005_1.inputs[3].default_value = 2
        # Socket_9
        group_005_1.inputs[4].default_value = True
        # Socket_10
        group_005_1.inputs[5].default_value = False
        # Socket_11
        group_005_1.inputs[6].default_value = False
        # Socket_12
        group_005_1.inputs[7].default_value = True
        # Socket_13
        group_005_1.inputs[8].default_value = False
        # Socket_14
        group_005_1.inputs[9].default_value = True

        # Node Switch
        switch_2 = geometry_nodes.nodes.new("GeometryNodeSwitch")
        switch_2.name = "Switch"
        switch_2.hide = True
        switch_2.input_type = "GEOMETRY"

        # Node Switch.001
        switch_001_1 = geometry_nodes.nodes.new("GeometryNodeSwitch")
        switch_001_1.name = "Switch.001"
        switch_001_1.hide = True
        switch_001_1.input_type = "GEOMETRY"

        # Node Switch.002
        switch_002 = geometry_nodes.nodes.new("GeometryNodeSwitch")
        switch_002.name = "Switch.002"
        switch_002.hide = True
        switch_002.input_type = "GEOMETRY"

        # Node Switch.003
        switch_003 = geometry_nodes.nodes.new("GeometryNodeSwitch")
        switch_003.name = "Switch.003"
        switch_003.hide = True
        switch_003.input_type = "GEOMETRY"

        # Node Switch.004
        switch_004 = geometry_nodes.nodes.new("GeometryNodeSwitch")
        switch_004.name = "Switch.004"
        switch_004.hide = True
        switch_004.input_type = "GEOMETRY"

        # Node Switch.005
        switch_005 = geometry_nodes.nodes.new("GeometryNodeSwitch")
        switch_005.name = "Switch.005"
        switch_005.hide = True
        switch_005.input_type = "GEOMETRY"

        # Node Group.006
        group_006_1 = geometry_nodes.nodes.new("GeometryNodeGroup")
        group_006_1.name = "Group.006"
        group_006_1.node_tree = outline

        # Node Group Input.001
        group_input_001 = geometry_nodes.nodes.new("NodeGroupInput")
        group_input_001.name = "Group Input.001"
        group_input_001.outputs[0].hide = True
        group_input_001.outputs[1].hide = True
        group_input_001.outputs[2].hide = True
        group_input_001.outputs[3].hide = True
        group_input_001.outputs[4].hide = True
        group_input_001.outputs[5].hide = True
        group_input_001.outputs[6].hide = True
        group_input_001.outputs[7].hide = True
        group_input_001.outputs[9].hide = True
        group_input_001.outputs[10].hide = True

        # Node Group Input.002
        group_input_002 = geometry_nodes.nodes.new("NodeGroupInput")
        group_input_002.name = "Group Input.002"
        group_input_002.outputs[0].hide = True
        group_input_002.outputs[1].hide = True
        group_input_002.outputs[2].hide = True
        group_input_002.outputs[3].hide = True
        group_input_002.outputs[4].hide = True
        group_input_002.outputs[5].hide = True
        group_input_002.outputs[6].hide = True
        group_input_002.outputs[7].hide = True
        group_input_002.outputs[8].hide = True
        group_input_002.outputs[10].hide = True

        # Set locations
        group_output_7.location = (762.880126953125, 284.71282958984375)
        group_input_7.location = (-982.1718139648438, 404.4394226074219)
        group_2.location = (-365.7976989746094, -47.921844482421875)
        join_geometry_3.location = (151.6416015625, 351.80767822265625)
        group_001_2.location = (-365.7976989746094, 72.59237670898438)
        group_002_1.location = (-365.7976989746094, 193.58123779296875)
        group_003_1.location = (-365.7976989746094, 305.9450988769531)
        group_004_1.location = (-365.7976989746094, 416.9327392578125)
        group_005_1.location = (-365.7976989746094, 521.9598388671875)
        switch_2.location = (-179.05787658691406, -13.140869140625)
        switch_001_1.location = (-179.05787658691406, 80.67352294921875)
        switch_002.location = (-179.05787658691406, 231.31231689453125)
        switch_003.location = (-179.05787658691406, 353.069580078125)
        switch_004.location = (-179.05787658691406, 461.35260009765625)
        switch_005.location = (-179.05787658691406, 524.0296020507812)
        group_006_1.location = (476.3335876464844, 286.5299987792969)
        group_input_001.location = (211.06448364257812, 227.47900390625)
        group_input_002.location = (207.85714721679688, 148.28985595703125)

        # Set dimensions
        group_output_7.width, group_output_7.height = 140.0, 100.0
        group_input_7.width, group_input_7.height = 140.0, 100.0
        group_2.width, group_2.height = 140.0, 100.0
        join_geometry_3.width, join_geometry_3.height = 140.0, 100.0
        group_001_2.width, group_001_2.height = 140.0, 100.0
        group_002_1.width, group_002_1.height = 140.0, 100.0
        group_003_1.width, group_003_1.height = 140.0, 100.0
        group_004_1.width, group_004_1.height = 140.0, 100.0
        group_005_1.width, group_005_1.height = 140.0, 100.0
        switch_2.width, switch_2.height = 140.0, 100.0
        switch_001_1.width, switch_001_1.height = 140.0, 100.0
        switch_002.width, switch_002.height = 140.0, 100.0
        switch_003.width, switch_003.height = 140.0, 100.0
        switch_004.width, switch_004.height = 140.0, 100.0
        switch_005.width, switch_005.height = 140.0, 100.0
        group_006_1.width, group_006_1.height = 140.0, 100.0
        group_input_001.width, group_input_001.height = 140.0, 100.0
        group_input_002.width, group_input_002.height = 140.0, 100.0

        # Initialize geometry_nodes links

        # group_006_1.Mesh -> group_output_7.Geometry
        geometry_nodes.links.new(group_006_1.outputs[0], group_output_7.inputs[0])
        # group_input_7.Sizes -> group_2.Sizes
        geometry_nodes.links.new(group_input_7.outputs[0], group_2.inputs[0])
        # group_input_7.Sizes -> group_001_2.Sizes
        geometry_nodes.links.new(group_input_7.outputs[0], group_001_2.inputs[0])
        # group_input_7.Deltas -> group_001_2.Deltas
        geometry_nodes.links.new(group_input_7.outputs[1], group_001_2.inputs[1])
        # group_input_7.Deltas -> group_2.Deltas
        geometry_nodes.links.new(group_input_7.outputs[1], group_2.inputs[1])
        # group_input_7.Sizes -> group_002_1.Sizes
        geometry_nodes.links.new(group_input_7.outputs[0], group_002_1.inputs[0])
        # group_input_7.Sizes -> group_003_1.Sizes
        geometry_nodes.links.new(group_input_7.outputs[0], group_003_1.inputs[0])
        # group_input_7.Deltas -> group_003_1.Deltas
        geometry_nodes.links.new(group_input_7.outputs[1], group_003_1.inputs[1])
        # group_input_7.Deltas -> group_002_1.Deltas
        geometry_nodes.links.new(group_input_7.outputs[1], group_002_1.inputs[1])
        # group_input_7.Sizes -> group_004_1.Sizes
        geometry_nodes.links.new(group_input_7.outputs[0], group_004_1.inputs[0])
        # group_input_7.Sizes -> group_005_1.Sizes
        geometry_nodes.links.new(group_input_7.outputs[0], group_005_1.inputs[0])
        # group_input_7.Deltas -> group_005_1.Deltas
        geometry_nodes.links.new(group_input_7.outputs[1], group_005_1.inputs[1])
        # group_input_7.Deltas -> group_004_1.Deltas
        geometry_nodes.links.new(group_input_7.outputs[1], group_004_1.inputs[1])
        # group_2.Mesh -> switch_2.True
        geometry_nodes.links.new(group_2.outputs[0], switch_2.inputs[2])
        # group_001_2.Mesh -> switch_001_1.True
        geometry_nodes.links.new(group_001_2.outputs[0], switch_001_1.inputs[2])
        # group_002_1.Mesh -> switch_002.True
        geometry_nodes.links.new(group_002_1.outputs[0], switch_002.inputs[2])
        # group_003_1.Mesh -> switch_003.True
        geometry_nodes.links.new(group_003_1.outputs[0], switch_003.inputs[2])
        # group_004_1.Mesh -> switch_004.True
        geometry_nodes.links.new(group_004_1.outputs[0], switch_004.inputs[2])
        # group_005_1.Mesh -> switch_005.True
        geometry_nodes.links.new(group_005_1.outputs[0], switch_005.inputs[2])
        # group_input_7.-Z -> switch_2.Switch
        geometry_nodes.links.new(group_input_7.outputs[7], switch_2.inputs[0])
        # group_input_7.+Z -> switch_001_1.Switch
        geometry_nodes.links.new(group_input_7.outputs[6], switch_001_1.inputs[0])
        # group_input_7.+Y -> switch_003.Switch
        geometry_nodes.links.new(group_input_7.outputs[4], switch_003.inputs[0])
        # group_input_7.-X -> switch_004.Switch
        geometry_nodes.links.new(group_input_7.outputs[3], switch_004.inputs[0])
        # group_input_7.+X -> switch_005.Switch
        geometry_nodes.links.new(group_input_7.outputs[2], switch_005.inputs[0])
        # group_input_7.-Y -> switch_002.Switch
        geometry_nodes.links.new(group_input_7.outputs[5], switch_002.inputs[0])
        # switch_2.Output -> join_geometry_3.Geometry
        geometry_nodes.links.new(switch_2.outputs[0], join_geometry_3.inputs[0])
        # join_geometry_3.Geometry -> group_006_1.Curve
        geometry_nodes.links.new(join_geometry_3.outputs[0], group_006_1.inputs[0])
        # group_input_001.Resolution -> group_006_1.Resolution
        geometry_nodes.links.new(group_input_001.outputs[8], group_006_1.inputs[1])
        # group_input_002.Radius -> group_006_1.Radius
        geometry_nodes.links.new(group_input_002.outputs[9], group_006_1.inputs[2])
        # switch_001_1.Output -> join_geometry_3.Geometry
        geometry_nodes.links.new(switch_001_1.outputs[0], join_geometry_3.inputs[0])
        # switch_002.Output -> join_geometry_3.Geometry
        geometry_nodes.links.new(switch_002.outputs[0], join_geometry_3.inputs[0])
        # switch_003.Output -> join_geometry_3.Geometry
        geometry_nodes.links.new(switch_003.outputs[0], join_geometry_3.inputs[0])
        # switch_004.Output -> join_geometry_3.Geometry
        geometry_nodes.links.new(switch_004.outputs[0], join_geometry_3.inputs[0])
        # switch_005.Output -> join_geometry_3.Geometry
        geometry_nodes.links.new(switch_005.outputs[0], join_geometry_3.inputs[0])

        return geometry_nodes

    return geometry_nodes_node_group()
