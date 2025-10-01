import bpy  # type: ignore
import bpy.utils.previews # type: ignore

import numpy as np  # type: ignore

COLORMAPS = {
    "fire": [
        (0.0, (0.0, 0.0, 0.0)),
        (0.0625, (0.19607843, 0.0, 0.0)),
        (0.125, (0.29019608, 0.0, 0.0)),
        (0.1875, (0.38823529, 0.00392157, 0.0)),
        (0.25, (0.49019608, 0.00784314, 0.0)),
        (0.3125, (0.59607843, 0.01176471, 0.0)),
        (0.375, (0.70588235, 0.01960784, 0.0)),
        (0.4375, (0.81960784, 0.03529412, 0.0)),
        (0.5, (0.92941176, 0.07843137, 0.0)),
        (0.5625, (0.98431373, 0.25098039, 0.0)),
        (0.625, (0.99607843, 0.40784314, 0.0)),
        (0.6875, (1.0, 0.5372549, 0.0)),
        (0.75, (1.0, 0.65098039, 0.00392157)),
        (0.8125, (1.0, 0.75686275, 0.01176471)),
        (0.875, (1.0, 0.85490196, 0.03529412)),
        (0.9375, (1.0, 0.95294118, 0.14117647)),
        (1.0, (1.0, 1.0, 1.0)),
    ],
    "viridis": [
        (0.0, (0.267004, 0.004874, 0.329415)),
        (0.0625, (0.282327, 0.094955, 0.417331)),
        (0.125, (0.278826, 0.17549, 0.483397)),
        (0.1875, (0.258965, 0.251537, 0.524736)),
        (0.25, (0.229739, 0.322361, 0.545706)),
        (0.3125, (0.19943, 0.387607, 0.554642)),
        (0.375, (0.172719, 0.448791, 0.557885)),
        (0.4375, (0.149039, 0.508051, 0.55725)),
        (0.5, (0.127568, 0.566949, 0.550556)),
        (0.5625, (0.120638, 0.625828, 0.533488)),
        (0.625, (0.157851, 0.683765, 0.501686)),
        (0.6875, (0.24607, 0.73891, 0.452024)),
        (0.75, (0.369214, 0.788888, 0.382914)),
        (0.8125, (0.515992, 0.831158, 0.294279)),
        (0.875, (0.678489, 0.863742, 0.189503)),
        (0.9375, (0.845561, 0.887322, 0.099702)),
        (1.0, (0.993248, 0.906157, 0.143936)),
    ],
    "plasma": [
        (0.0, (0.050383, 0.029803, 0.527975)),
        (0.0625, (0.193374, 0.018354, 0.59033)),
        (0.125, (0.299855, 0.009561, 0.631624)),
        (0.1875, (0.399411, 0.000859, 0.656133)),
        (0.25, (0.494877, 0.01199, 0.657865)),
        (0.3125, (0.584391, 0.068579, 0.632812)),
        (0.375, (0.665129, 0.138566, 0.585582)),
        (0.4375, (0.736019, 0.209439, 0.527908)),
        (0.5, (0.798216, 0.280197, 0.469538)),
        (0.5625, (0.853319, 0.351553, 0.413734)),
        (0.625, (0.901807, 0.425087, 0.359688)),
        (0.6875, (0.942598, 0.502639, 0.305816)),
        (0.75, (0.973416, 0.585761, 0.25154)),
        (0.8125, (0.991365, 0.675355, 0.198453)),
        (0.875, (0.993033, 0.77172, 0.154808)),
        (0.9375, (0.974443, 0.874622, 0.144061)),
        (1.0, (0.940015, 0.975158, 0.131326)),
    ],
    "inferno": [
        (0.0, (0.001462, 0.000466, 0.013866)),
        (0.0625, (0.042253, 0.028139, 0.141141)),
        (0.125, (0.129285, 0.047293, 0.290788)),
        (0.1875, (0.238273, 0.036621, 0.396353)),
        (0.25, (0.3415, 0.062325, 0.429425)),
        (0.3125, (0.441207, 0.099338, 0.431594)),
        (0.375, (0.54092, 0.134729, 0.415123)),
        (0.4375, (0.640135, 0.171438, 0.381065)),
        (0.5, (0.735683, 0.215906, 0.330245)),
        (0.5625, (0.822386, 0.275197, 0.266085)),
        (0.625, (0.894305, 0.353399, 0.193584)),
        (0.6875, (0.946965, 0.449191, 0.115272)),
        (0.75, (0.978422, 0.557937, 0.034931)),
        (0.8125, (0.987874, 0.675267, 0.065257)),
        (0.875, (0.974638, 0.797692, 0.206332)),
        (0.9375, (0.947594, 0.917399, 0.410665)),
        (1.0, (0.988362, 0.998364, 0.644924)),
    ],
    "magma": [
        (0.0, (0.001462, 0.000466, 0.013866)),
        (0.0625, (0.039608, 0.03109, 0.133515)),
        (0.125, (0.113094, 0.065492, 0.276784)),
        (0.1875, (0.211718, 0.061992, 0.418647)),
        (0.25, (0.316654, 0.07169, 0.48538)),
        (0.3125, (0.414709, 0.110431, 0.504662)),
        (0.375, (0.512831, 0.148179, 0.507648)),
        (0.4375, (0.613617, 0.181811, 0.498536)),
        (0.5, (0.716387, 0.214982, 0.47529)),
        (0.5625, (0.816914, 0.255895, 0.436461)),
        (0.625, (0.904281, 0.31961, 0.388137)),
        (0.6875, (0.960949, 0.418323, 0.35963)),
        (0.75, (0.9867, 0.535582, 0.38221)),
        (0.8125, (0.996096, 0.653659, 0.446213)),
        (0.875, (0.996898, 0.769591, 0.534892)),
        (0.9375, (0.99244, 0.88433, 0.640099)),
        (1.0, (0.987053, 0.991438, 0.749504)),
    ],
    "jet": [
        (0.0, (0.0, 0.0, 0.5)),
        (0.0625, (0.0, 0.0, 0.785204991087344)),
        (0.125, (0.0, 0.00196078431372549, 1.0)),
        (0.1875, (0.0, 0.2529411764705882, 1.0)),
        (0.25, (0.0, 0.503921568627451, 1.0)),
        (0.3125, (0.0, 0.7549019607843137, 1.0)),
        (0.375, (0.08538899430740036, 1.0, 0.8823529411764706)),
        (0.4375, (0.2877925363693864, 1.0, 0.6799493991144845)),
        (0.5, (0.4901960784313725, 1.0, 0.4775458570524984)),
        (0.5625, (0.6925996204933585, 1.0, 0.27514231499051234)),
        (0.625, (0.8950031625553446, 1.0, 0.07273877292852626)),
        (0.6875, (1.0, 0.8140885984023241, 0.0)),
        (0.75, (1.0, 0.5816993464052289, 0.0)),
        (0.8125, (1.0, 0.34931009440813376, 0.0)),
        (0.875, (1.0, 0.11692084241103862, 0.0)),
        (0.9375, (0.7673796791443852, 0.0, 0.0)),
        (1.0, (0.5, 0.0, 0.0)),
    ],
    "turbo": [
        (0.0, (0.18995, 0.07176, 0.23217)),
        (0.0625, (0.25107, 0.25237, 0.63374)),
        (0.125, (0.27628, 0.42118, 0.89123)),
        (0.1875, (0.25862, 0.57958, 0.99876)),
        (0.25, (0.15844, 0.73551, 0.92305)),
        (0.3125, (0.09267, 0.86554, 0.7623)),
        (0.375, (0.19659, 0.94901, 0.59466)),
        (0.4375, (0.42778, 0.99419, 0.38575)),
        (0.5, (0.64362, 0.98999, 0.23356)),
        (0.5625, (0.80473, 0.92452, 0.20459)),
        (0.625, (0.93301, 0.81236, 0.22667)),
        (0.6875, (0.99314, 0.67408, 0.20348)),
        (0.75, (0.9836, 0.49291, 0.12849)),
        (0.8125, (0.92105, 0.31489, 0.05475)),
        (0.875, (0.81608, 0.18462, 0.01809)),
        (0.9375, (0.66449, 0.08436, 0.00424)),
        (1.0, (0.4796, 0.01583, 0.01055)),
    ],
    "twilight": [
        (0.0, (0.8857501584075443, 0.8500092494306783, 0.8879736506427196)),
        (0.0625, (0.7675110850441786, 0.8098007598713145, 0.8325281663805967)),
        (0.125, (0.5830148703693241, 0.7095888767699747, 0.7792578182047659)),
        (0.1875, (0.4480247093358917, 0.5923833145214658, 0.7557417647410792)),
        (0.25, (0.38407269378943537, 0.46139018782416635, 0.7309466543290268)),
        (0.3125, (0.3698798032902536, 0.31638410101153364, 0.6770375543809057)),
        (0.375, (0.3506030444193101, 0.1659512998472086, 0.5614796470399323)),
        (0.4375, (0.2700863774911405, 0.07548367558427554, 0.36056376228111864)),
        (0.5, (0.18488035509396164, 0.07942573027972388, 0.21307651648984993)),
        (0.5625, (0.29128515387578635, 0.0748990498474667, 0.25755101595750435)),
        (0.625, (0.4538300508699989, 0.11622183788331528, 0.3097044124984492)),
        (0.6875, (0.5965991810912237, 0.207212956082026, 0.3125852303112123)),
        (0.75, (0.6980608153581771, 0.3382897632604862, 0.3220747885521809)),
        (0.8125, (0.7625733355405261, 0.48718906673415824, 0.38675335037837993)),
        (0.875, (0.8002941538975398, 0.6409821330674986, 0.5373053518514104)),
        (0.9375, (0.8489224556311764, 0.7799202140765015, 0.7466371929366437)),
        (1.0, (0.8857115512284565, 0.8500218611585632, 0.8857253899008712)),
    ],
    "RdBu": [
        (0.0, (0.403921568627451, 0.0, 0.12156862745098039)),
        (0.0625, (0.5884659746251442, 0.05905420991926182, 0.1510957324106113)),
        (0.125, (0.7340253748558246, 0.16608996539792387, 0.20261437908496732)),
        (0.1875, (0.8226066897347174, 0.34325259515570933, 0.28627450980392155)),
        (0.25, (0.8991926182237601, 0.5144175317185697, 0.4079200307574009)),
        (0.3125, (0.9617070357554787, 0.6761245674740484, 0.546943483275663)),
        (0.375, (0.9838523644752019, 0.8089965397923875, 0.7167243367935409)),
        (0.4375, (0.9829296424452134, 0.9018838908112264, 0.8542099192618224)),
        (0.5, (0.9657054978854287, 0.9672433679354094, 0.9680891964628989)),
        (0.5625, (0.8722029988465976, 0.9229527104959632, 0.9508650519031142)),
        (0.625, (0.7517877739331029, 0.8635909265667053, 0.9217993079584775)),
        (0.6875, (0.5967704728950406, 0.7848519800076895, 0.8775086505190313)),
        (0.75, (0.4085351787773935, 0.6687427912341408, 0.8145328719723184)),
        (0.8125, (0.24183006535947713, 0.5487889273356401, 0.750557477893118)),
        (0.875, (0.15816993464052287, 0.43806228373702427, 0.6939638600538255)),
        (0.9375, (0.08419838523644753, 0.31280276816609, 0.5534025374855824)),
        (1.0, (0.0196078431372549, 0.18823529411764706, 0.3803921568627451)),
    ],
    "BrBG": [
        (0.0, (0.32941176470588235, 0.18823529411764706, 0.0196078431372549)),
        (0.0625, (0.46720492118415996, 0.26943483275663205, 0.031910803537101115)),
        (0.125, (0.6000000000000001, 0.3656286043829296, 0.07420222991157246)),
        (0.1875, (0.7254901960784313, 0.48373702422145326, 0.16032295271049596)),
        (0.25, (0.8129950019223375, 0.635832372164552, 0.33640907343329485)),
        (0.3125, (0.8868896578239138, 0.7812379853902344, 0.5278738946559014)),
        (0.375, (0.9434832756632064, 0.8747404844290657, 0.7001153402537484)),
        (0.4375, (0.9631680123029605, 0.9297962322183776, 0.84159938485198)),
        (0.5, (0.9572472126105345, 0.9599384851980008, 0.9595540176855056)),
        (0.5625, (0.8440599769319495, 0.9328719723183391, 0.9201845444059977)),
        (0.625, (0.7039600153787008, 0.8864282968089198, 0.8592848904267592)),
        (0.6875, (0.5292579777008846, 0.8150711264898117, 0.7707035755478664)),
        (0.75, (0.346251441753172, 0.6918108419838525, 0.653056516724337)),
        (0.8125, (0.1758554402153018, 0.5620146097654748, 0.530642060745867)),
        (0.875, (0.0479046520569012, 0.44144559784698195, 0.4100730488273741)),
        (0.9375, (0.002306805074971165, 0.33217993079584773, 0.2943483275663207)),
        (1.0, (0.0, 0.23529411764705882, 0.18823529411764706)),
    ],
}


def _resolve_cmap_id(val):
    # Convert whatever the property gives us into a valid identifier string.
    if isinstance(val, str):
        return val
    ids = list(COLORMAPS.keys())
    try:
        idx = int(val)
    except (TypeError, ValueError):
        idx = 0
    if 0 <= idx < len(ids):
        return ids[idx]
    # Fallback
    return next(iter(COLORMAPS.keys()), "Default")


_PREVIEW_COLLECTIONS = {}


def Build_colormap_previews():
    if "colormaps" in _PREVIEW_COLLECTIONS:
        return _PREVIEW_COLLECTIONS["colormaps"]

    def _lerp(a, b, t):
        return a + (b - a) * t

    def _sample_stops(stops, t):
        """Return (r,g,b,a) at t in [0..1] by linear interpolation of stops."""

        s = sorted(stops, key=lambda x: x[0])
        if t <= s[0][0]:
            c = s[0][1]
            return (c[0], c[1], c[2], c[3] if len(c) > 3 else 1.0)
        for i in range(len(s) - 1):
            t0, c0 = s[i]
            t1, c1 = s[i + 1]
            if t <= t1 or i == len(s) - 2:
                u = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
                a0 = c0[3] if len(c0) > 3 else 1.0
                a1 = c1[3] if len(c1) > 3 else 1.0
                return (
                    _lerp(c0[0], c1[0], u),
                    _lerp(c0[1], c1[1], u),
                    _lerp(c0[2], c1[2], u),
                    _lerp(a0, a1, u),
                )
        c = s[-1][1]
        return (c[0], c[1], c[2], c[3] if len(c) > 3 else 1.0)

    def _render_gradient_pixels(stops, w, h, vertical=False):

        px = [0.0] * (w * h * 4)
        for y in range(h):
            for x in range(w):
                t = (y / (h - 1)) if vertical else (x / (w - 1))
                r, g, b, a = _sample_stops(stops, t)
                i = (y * w + x) * 4
                px[i : i + 4] = (r, g, b, a)
        return px

    pcoll = bpy.utils.previews.new()
    img_w, img_h = 128, 32
    ico_w, ico_h = 64, 64
    for cm_id, stops in COLORMAPS.items():
        p = pcoll.new(cm_id)
        p.image_size = (img_w, img_h)
        p.image_pixels_float[:] = _render_gradient_pixels(stops, img_w, img_h)
        p.icon_size = (ico_w, ico_h)
        p.icon_pixels_float[:] = _render_gradient_pixels(stops, ico_w, ico_h)
    _PREVIEW_COLLECTIONS["colormaps"] = pcoll
    return pcoll


def Free_colormap_previews():
    for pcoll in _PREVIEW_COLLECTIONS.values():
        bpy.utils.previews.remove(pcoll)
    _PREVIEW_COLLECTIONS.clear()


def _static_enum_items():
    # Always valid, even if previews aren't built yet.
    # Uses a built-in icon ('COLOR') as a fallback.
    ids = list(COLORMAPS.keys())
    if not ids:
        return [("Default", "Default", "Colormap", "COLOR", 0)]
    return [(cm_id, cm_id, "Colormap", "COLOR", i) for i, cm_id in enumerate(ids)]


def Enum_colormap_items(self, context):
    """
    Dynamic items for the EnumProperty. If preview icons are not ready yet
    (e.g., during initial registration), fall back to static items so the
    property can register successfully.
    """
    try:
        pcoll = _PREVIEW_COLLECTIONS.get("colormaps", None)
        if pcoll is None:
            # Previews not built yet (or freed) -> safe fallback (no gradients)
            return _static_enum_items()

        items = []
        ids = list(COLORMAPS.keys())
        for i, cm_id in enumerate(ids):
            # If the preview is missing for any reason, fall back to a built-in icon.
            ip = pcoll.get(cm_id)
            icon = (ip.icon_id if ip else 0) or "COLOR"
            items.append((cm_id, cm_id, "Colormap", icon, i))

        # If COLORMAPS is empty or something went wrong, never return [].
        return items or _static_enum_items()

    except Exception as e:
        print(f"enum_colormap_items fallback due to error: {e}")
        return _static_enum_items()


def _apply_stops_to_colorramp(ramp: bpy.types.ColorRamp, stops):
    s = sorted(stops, key=lambda x: x[0])
    # Ensure correct count
    while len(ramp.elements) > len(s):
        ramp.elements.remove(ramp.elements[-1])
    while len(ramp.elements) < len(s):
        ramp.elements.new(0.5)
    # Write positions/colors
    for elem, (t, col) in zip(ramp.elements, s):
        elem.position = max(0.0, min(1.0, float(t)))
        if len(col) == 4:
            elem.color = col
        else:
            r, g, b = col
            elem.color = (r, g, b, 1.0)
    ramp.color_mode = "RGB"
    ramp.interpolation = "LINEAR"


def _stops_for_colormap(cm_id, reverse=False):
    """Return the stop list for a given colormap id, optionally reversed (_r style)."""
    # Fallback to the first map if id is missing
    first = next(iter(COLORMAPS.keys()))
    stops = COLORMAPS.get(cm_id, COLORMAPS[first])
    if not reverse:
        return stops
    # Reverse: color at 1 - t. Keep stops sorted ascending after transform.
    rev = [(1.0 - t, col) for (t, col) in reversed(stops)]
    rev.sort(key=lambda x: x[0])
    return rev


def Create_or_reset_volume_material(name) -> bpy.types.Material:
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
    else:
        if not mat.use_nodes:
            mat.use_nodes = True

    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links

    def _get_or_new(nodes, type_id, name=None, label=None):
        n = nodes.get(name) if name else None
        if n is None:
            n = nodes.new(type_id)
            if name:
                n.name = name
            if label:
                n.label = label
        return n

    vol_info = _get_or_new(nodes, "ShaderNodeVolumeInfo", "VolumeInfo", "Volume info")
    vol_info.location = (-50, -100)

    map_range = _get_or_new(nodes, "ShaderNodeMapRange", "ValueRemap", "Remap values")
    map_range.location = (150, 0)

    color_ramp = _get_or_new(nodes, "ShaderNodeValToRGB", "Colormap", "Colormap")
    color_ramp.location = (400, 300)

    float_curve = _get_or_new(
        nodes, "ShaderNodeFloatCurve", "OpacityCurve", "Opacity curve"
    )
    float_curve.location = (400, 0)

    multiply_1 = _get_or_new(
        nodes, "ShaderNodeMath", "MultiplyEmissivity", "Emissivity multiplier"
    )
    multiply_1.location = (400, -400)
    multiply_1.operation = "MULTIPLY"
    multiply_1.inputs[1].default_value = 2.0

    multiply_2 = _get_or_new(
        nodes, "ShaderNodeMath", "MultiplyOpacity", "Opacity multiplier"
    )
    multiply_2.location = (800, 0)
    multiply_2.operation = "MULTIPLY"
    multiply_2.inputs[1].default_value = 1.0

    vol = _get_or_new(nodes, "ShaderNodeVolumePrincipled", "Volume", "Volume shader")
    vol.location = (1100, 100)

    out = _get_or_new(
        nodes, "ShaderNodeOutputMaterial", "MaterialOutput", "Material Output"
    )
    out.location = (1400, 100)

    def _link_if_missing(a, b):
        if not b.links or all(l.from_socket is not a for l in b.links):
            links.new(a, b)

    _link_if_missing(vol_info.outputs["Density"], map_range.inputs["Value"])
    _link_if_missing(map_range.outputs["Result"], color_ramp.inputs["Fac"])
    _link_if_missing(map_range.outputs["Result"], float_curve.inputs["Value"])
    _link_if_missing(map_range.outputs["Result"], multiply_1.inputs[0])
    _link_if_missing(float_curve.outputs["Value"], multiply_2.inputs[0])
    _link_if_missing(color_ramp.outputs["Color"], vol.inputs["Color"])
    _link_if_missing(color_ramp.outputs["Color"], vol.inputs["Emission Color"])
    _link_if_missing(multiply_1.outputs["Value"], vol.inputs["Emission Strength"])
    _link_if_missing(multiply_2.outputs["Value"], vol.inputs["Density"])
    _link_if_missing(vol.outputs["Volume"], out.inputs["Volume"])

    cm_id = _resolve_cmap_id(getattr(mat, "volume_colormap", 0))
    rev = bool(getattr(mat, "volume_colormap_reversed", False))
    _apply_stops_to_colorramp(
        color_ramp.color_ramp, _stops_for_colormap(cm_id, reverse=rev)
    )

    return mat


def Store_histogram_on_material(
    mat: bpy.types.Material,
    hist: np.ndarray,
    vmin: float,
    vmax: float,
    q05: float,
    q95: float,
    width: int = 256,
    height: int = 256,
):
    bins = int(hist.size)
    # --- draw pixels ---
    px = np.empty((height, width, 4), dtype=np.float32)

    px[..., 0:3] = 0.22
    px[..., 3] = 1.0

    hmax = int(hist.max()) if hist.size else 1
    if hmax < 1:
        hmax = 1

    # normalized heights (0..H-10)
    heights = np.ceil((hist.astype(np.float32) / float(hmax)) * (height - 10)).astype(
        np.int32
    )

    # draw per-bin rectangles with >=2 px width
    for i in range(bins):
        x0 = int(i * width / bins)
        x1 = int((i + 1) * width / bins)
        if x1 <= x0:
            x1 = x0 + 1
        # ensure visible min width
        if x1 - x0 < 2:
            x1 = x0 + 2 if x0 + 2 <= width else width

        h = int(heights[i])
        if h > 0:
            px[0:h, x0:x1, 0:3] = 0.98
            px[0:h, x0:x1, 3] = 1.0

    if vmin < q05 < vmax:
        iq05 = int((q05 - vmin) / (vmax - vmin) * width)
        px[:, iq05 : min(iq05 + 2, width), 0] = 1.0
        px[:, iq05 : min(iq05 + 2, width), 1:3] = 0.2
        px[:, iq05 : min(iq05 + 2, width), 3] = 1.0

    if vmin < q95 < vmax:
        iq95 = int((q95 - vmin) / (vmax - vmin) * width)
        px[:, iq95 : min(iq95 + 2, width), 0] = 1.0
        px[:, iq95 : min(iq95 + 2, width), 1:3] = 0.2
        px[:, iq95 : min(iq95 + 2, width), 3] = 1.0

    img_name = f"SB_Hist_{mat.name}"
    img = bpy.data.images.get(img_name)
    if img is None:
        img = bpy.data.images.new(
            img_name, width=width, height=height, alpha=True, float_buffer=True
        )
        img.colorspace_settings.name = "Non-Color"
        img.alpha_mode = "STRAIGHT"
        img.use_fake_user = True
    else:
        if img.size[0] != width or img.size[1] != height:
            img.scale(width, height)

    img.pixels[:] = px.ravel().tolist()
    img.update()
    img.preview_ensure()

    # Store on the material
    mat.volume_hist_vmin = float(vmin)
    mat.volume_hist_vmax = float(vmax)
    mat.volume_hist_q05 = float(q05)
    mat.volume_hist_q95 = float(q95)
    mat.volume_hist_image = img
    mat.volume_hist_ready = True


def Clear_histogram_on_material(mat: bpy.types.Material):
    mat.volume_hist_vmin = 0.0
    mat.volume_hist_vmax = 0.0
    mat.volume_hist_q05 = 0.0
    mat.volume_hist_q95 = 0.0
    mat.volume_hist_image = None
    mat.volume_hist_ready = False


def Create_volume_object(context, store_path, abspath, uuid_str):
    scene = context.scene
    display_name = bpy.path.display_name_from_filepath(abspath)
    base_name = f"{display_name}_Volume_{uuid_str}"

    vol_data = bpy.data.volumes.new(name=base_name)
    vol_data.filepath = store_path

    vol_obj = bpy.data.objects.new(base_name, vol_data)
    collection = context.collection or context.scene.collection
    collection.objects.link(vol_obj)
    vol_obj.location = scene.cursor.location
    vol_obj.scale = (0.01, 0.01, 0.01)

    active_obj = vol_obj
    bpy.ops.object.select_all(action="DESELECT")
    active_obj.select_set(True)
    context.view_layer.objects.active = active_obj

    mat = Create_or_reset_volume_material(f"{display_name}_Material_{uuid_str}")
    if len(vol_obj.data.materials) == 0:
        vol_obj.data.materials.append(mat)
    else:
        vol_obj.data.materials[0] = mat

    return base_name, display_name, mat


def On_material_colormap_change(self, context):
    """Update callback: self is the Material that owns 'volume_colormap'."""
    if not getattr(self, "use_nodes", False) or not self.node_tree:
        return None
    nt = self.node_tree
    ramp_node = nt.nodes.get("Colormap")
    if ramp_node is None or ramp_node.type != "VALTORGB":
        # Make sure nodes exist and try again
        Create_or_reset_volume_material(self.name)
        ramp_node = nt.nodes.get("Colormap")
    if ramp_node:
        cm_id = _resolve_cmap_id(getattr(self, "volume_colormap", 0))
        rev = bool(getattr(self, "volume_colormap_reversed", False))
        stops = _stops_for_colormap(cm_id, reverse=rev)
        _apply_stops_to_colorramp(ramp_node.color_ramp, stops)
    return None
