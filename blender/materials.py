# Procedural Cycles materials for the doors. They are baked to textures by common.bake_to_textures before export,
# so they may use any node. All patterns use Object coordinates in metres: X across the door, Z up.
import bpy, math
from common import rgb


class Graph:
    """Small wrapper that makes node graphs shorter to write."""

    def __init__(self, name):
        self.mat = bpy.data.materials.new(name)
        self.mat.use_nodes = True
        self.nt = self.mat.node_tree
        self.bsdf = self.nt.nodes.get('Principled BSDF')
        self.coord = self.nt.nodes.new('ShaderNodeTexCoord')
        self.obj = self.coord.outputs['Object']

    def node(self, kind, **props):
        n = self.nt.nodes.new(kind)
        for k, v in props.items():
            setattr(n, k, v)
        return n

    def link(self, a, b):
        self.nt.links.new(a, b)

    def put(self, socket, value):
        """Connect a socket, or set a constant."""
        if hasattr(value, 'is_linked') or hasattr(value, 'links'):
            self.link(value, socket)
        else:
            socket.default_value = value

    def math(self, op, a, b=None, clamp=False):
        n = self.node('ShaderNodeMath', operation=op, use_clamp=clamp)
        self.put(n.inputs[0], a)
        if b is not None:
            self.put(n.inputs[1], b)
        return n.outputs[0]

    def mapping(self, scale=(1, 1, 1), rot=(0, 0, 0), vector=None):
        n = self.node('ShaderNodeMapping')
        n.inputs['Scale'].default_value = scale
        n.inputs['Rotation'].default_value = rot
        self.link(vector or self.obj, n.inputs['Vector'])
        return n.outputs['Vector']

    def noise(self, scale, detail=6.0, rough=0.6, distortion=0.0, vector=None):
        n = self.node('ShaderNodeTexNoise')
        n.inputs['Scale'].default_value = scale
        n.inputs['Detail'].default_value = detail
        n.inputs['Roughness'].default_value = rough
        n.inputs['Distortion'].default_value = distortion
        self.link(vector or self.obj, n.inputs['Vector'])
        return n.outputs['Fac']

    def voronoi(self, scale, feature='F1', vector=None):
        n = self.node('ShaderNodeTexVoronoi', feature=feature)
        n.inputs['Scale'].default_value = scale
        self.link(vector or self.obj, n.inputs['Vector'])
        return n.outputs['Distance']

    def ramp(self, fac, stops):
        """stops: [(position, '#RRGGBB' or grey float), ...]"""
        n = self.node('ShaderNodeValToRGB')
        cr = n.color_ramp
        while len(cr.elements) < len(stops):
            cr.elements.new(0.5)
        for el, (pos, col) in zip(cr.elements, stops):
            el.position = pos
            el.color = rgb(col) if isinstance(col, str) else (col, col, col, 1.0)
        self.put(n.inputs['Fac'], fac)
        return n.outputs['Color']

    def mix(self, fac, a, b, mode='MIX'):
        """Mix two colours. a and b may be sockets, '#RRGGBB' strings or RGBA tuples."""
        n = self.node('ShaderNodeMix', data_type='RGBA', blend_type=mode)
        self.put(n.inputs[0], fac)
        for sock, v in ((n.inputs[6], a), (n.inputs[7], b)):
            self.put(sock, rgb(v) if isinstance(v, str) else v)
        return n.outputs[2]

    def smooth_step(self, value, lo, hi, out_lo=0.0, out_hi=1.0):
        n = self.node('ShaderNodeMapRange', interpolation_type='SMOOTHSTEP')
        self.put(n.inputs['Value'], value)
        n.inputs['From Min'].default_value = lo; n.inputs['From Max'].default_value = hi
        n.inputs['To Min'].default_value = out_lo; n.inputs['To Max'].default_value = out_hi
        return n.outputs['Result']

    def axis(self, name, vector=None):
        n = self.node('ShaderNodeSeparateXYZ')
        self.link(vector or self.obj, n.inputs[0])
        return n.outputs[name]

    def finish(self, colour, rough, metal=0.0, height=None, bump=0.5, distance=0.02):
        self.put(self.bsdf.inputs['Base Color'], rgb(colour) if isinstance(colour, str) else colour)
        self.put(self.bsdf.inputs['Roughness'], rough)
        self.put(self.bsdf.inputs['Metallic'], metal)
        if height is not None:
            b = self.node('ShaderNodeBump')
            b.inputs['Strength'].default_value = bump
            b.inputs['Distance'].default_value = distance
            self.link(height, b.inputs['Height'])
            self.link(b.outputs['Normal'], self.bsdf.inputs['Normal'])
        return self.mat


def plain(name, colour, rough=0.4, metal=0.0):
    """One flat colour, for small painted parts."""
    return Graph(name).finish(colour, rough, metal)


def wood(name, light, dark, plank=0.17, paint=None, wear=0.42, gloss=0.6):
    """Vertical planks with grain. paint: colour of an old coat of paint that has worn off in patches."""
    g = Graph(name)
    x = g.axis('X')
    cell = g.math('DIVIDE', x, plank)
    index = g.math('FLOOR', cell)
    across = g.math('FRACT', cell)
    edge = g.math('MINIMUM', across, g.math('SUBTRACT', 1.0, across))            # 0 at the gap between two planks
    gap = g.smooth_step(edge, 0.0, 0.045, 1.0, 0.0)

    # every plank gets its own tone and its own piece of grain
    shift = g.node('ShaderNodeCombineXYZ')
    g.link(g.math('MULTIPLY', index, 7.31), shift.inputs['Z'])
    g.link(g.math('MULTIPLY', index, 3.17), shift.inputs['X'])
    moved = g.node('ShaderNodeVectorMath', operation='ADD')
    g.link(g.obj, moved.inputs[0]); g.link(shift.outputs[0], moved.inputs[1])
    long_grain = g.mapping(scale=(26.0, 26.0, 1.6), vector=moved.outputs[0])
    grain = g.noise(1.0, detail=8.0, rough=0.62, distortion=1.2, vector=long_grain)
    tone = g.node('ShaderNodeTexWhiteNoise', noise_dimensions='1D')
    g.link(index, tone.inputs['W'])
    colour = g.ramp(grain, [(0.25, dark), (0.75, light)])
    colour = g.mix(g.math('MULTIPLY', tone.outputs['Value'], 0.35), colour, dark)
    height = g.math('MULTIPLY', grain, 0.35)
    rough = 0.72

    if paint:
        patches = g.noise(2.4, detail=7.0, rough=0.7, distortion=0.4)
        scratched = g.math('ADD', patches, g.math('MULTIPLY', grain, 0.22))
        coat = g.smooth_step(scratched, wear, wear + 0.08)                        # 1 where the paint is still there
        coat = g.math('MULTIPLY', coat, g.math('SUBTRACT', 1.0, g.math('MULTIPLY', gap, 0.9)))
        faded = g.mix(g.noise(1.1, detail=3.0), paint, '#FFFFFF')
        faded = g.mix(0.82, faded, paint)
        colour = g.mix(coat, colour, faded)
        height = g.math('ADD', height, g.math('MULTIPLY', coat, 0.45))
        rough = g.math('SUBTRACT', 0.74, g.math('MULTIPLY', coat, 0.74 - gloss))

    colour = g.mix(g.math('MULTIPLY', gap, 0.9), colour, '#120C07')
    height = g.math('SUBTRACT', height, g.math('MULTIPLY', gap, 1.6))
    return g.finish(colour, rough, 0.0, height, bump=0.55, distance=0.012)


def stone_blocks(name, light, dark, mortar, block=(0.62, 0.36), rough=0.86):
    """Cut stone blocks with mortar joints, seen from the front (pattern in the XZ plane)."""
    g = Graph(name)
    flat = g.mapping(rot=(math.radians(90), 0, 0))                                # brick texture draws in XY: turn Z into Y
    b = g.node('ShaderNodeTexBrick')
    b.offset = 0.5
    b.inputs['Scale'].default_value = 1.0
    b.inputs['Mortar Size'].default_value = 0.012
    b.inputs['Mortar Smooth'].default_value = 0.6
    b.inputs['Bias'].default_value = 0.0
    b.inputs['Brick Width'].default_value = block[0]
    b.inputs['Row Height'].default_value = block[1]
    b.inputs['Color1'].default_value = rgb(light)
    b.inputs['Color2'].default_value = rgb(dark)
    b.inputs['Mortar'].default_value = rgb(mortar)
    g.link(flat, b.inputs['Vector'])
    joint = b.outputs['Fac']
    cloudy = g.noise(3.2, detail=8.0, rough=0.68)
    speck = g.noise(58.0, detail=3.0, rough=0.8)
    colour = g.mix(g.math('MULTIPLY', cloudy, 0.55), b.outputs['Color'], dark)
    colour = g.mix(g.smooth_step(speck, 0.56, 0.72, 0.0, 0.35), colour, '#2A2622')
    pits = g.smooth_step(g.voronoi(34.0), 0.0, 0.16, 1.0, 0.0)
    height = g.math('SUBTRACT', g.math('ADD', g.math('MULTIPLY', cloudy, 0.5), g.math('MULTIPLY', speck, 0.2)),
                    g.math('ADD', g.math('MULTIPLY', joint, 1.4), g.math('MULTIPLY', pits, 0.5)))
    return g.finish(colour, rough, 0.0, height, bump=0.6, distance=0.014)


def granite(name, base, speck_light, speck_dark, rough=0.42):
    """Polished speckled stone, in blocks with thin joints."""
    g = Graph(name)
    flat = g.mapping(rot=(math.radians(90), 0, 0))
    b = g.node('ShaderNodeTexBrick')
    b.offset = 0.5
    b.inputs['Scale'].default_value = 1.0
    b.inputs['Mortar Size'].default_value = 0.008
    b.inputs['Mortar Smooth'].default_value = 0.4
    b.inputs['Bias'].default_value = 0.0
    b.inputs['Brick Width'].default_value = 0.9
    b.inputs['Row Height'].default_value = 0.45
    b.inputs['Color1'].default_value = (1, 1, 1, 1)
    b.inputs['Color2'].default_value = (0.82, 0.82, 0.82, 1)
    b.inputs['Mortar'].default_value = (0.2, 0.2, 0.2, 1)
    g.link(flat, b.inputs['Vector'])
    grains = g.voronoi(95.0)
    fine = g.noise(140.0, detail=2.0, rough=0.9)
    veins = g.noise(2.0, detail=9.0, rough=0.7, distortion=1.6)
    colour = g.mix(g.smooth_step(grains, 0.25, 0.6), speck_dark, base)
    colour = g.mix(g.smooth_step(fine, 0.6, 0.75, 0.0, 0.8), colour, speck_light)
    colour = g.mix(g.smooth_step(veins, 0.54, 0.62, 0.0, 0.16), colour, speck_light)
    colour = g.mix(1.0, colour, b.outputs['Color'], mode='MULTIPLY')
    height = g.math('SUBTRACT', g.math('MULTIPLY', fine, 0.08), g.math('MULTIPLY', b.outputs['Fac'], 1.2))
    return g.finish(colour, g.math('ADD', rough, g.math('MULTIPLY', b.outputs['Fac'], 0.4)), 0.0, height, bump=0.4, distance=0.01)


def metal(name, colour, rough=0.32, dirt=None, brushed=True, hammered=False):
    """Metal: brushed (fine vertical lines), hammered (wrought iron), with optional dirt or rust in patches."""
    g = Graph(name)
    patches = g.noise(5.5, detail=7.0, rough=0.7)
    col = rgb(colour)
    metalness = 1.0
    roughness = g.math('ADD', rough, g.math('MULTIPLY', g.math('SUBTRACT', patches, 0.5), 0.22))
    height = None
    if brushed:
        lines = g.noise(1.0, detail=2.0, rough=0.5, vector=g.mapping(scale=(240.0, 240.0, 2.5)))
        height = g.math('MULTIPLY', lines, 0.12)
    if hammered:
        dents = g.voronoi(38.0, feature='SMOOTH_F1')
        height = g.math('MULTIPLY', dents, 0.9)
    if dirt:
        mask = g.smooth_step(patches, 0.54, 0.68)
        col = g.mix(mask, colour, dirt)
        metalness = g.math('SUBTRACT', 1.0, g.math('MULTIPLY', mask, 0.75))
        roughness = g.math('ADD', roughness, g.math('MULTIPLY', mask, 0.4))
    return g.finish(col, roughness, metalness, height, bump=0.35, distance=0.006)


def frosted_glass(name, tint='#DCEFFB', frost='#FFFFFF'):
    """A pane of glass covered in frost: ice crystals growing from the edges, clearer in the middle."""
    g = Graph(name)
    crystals = g.voronoi(46.0, feature='DISTANCE_TO_EDGE')
    ferns = g.noise(9.0, detail=10.0, rough=0.78, distortion=2.2)
    cover = g.smooth_step(g.math('ADD', ferns, g.math('MULTIPLY', g.noise(1.4, detail=2.0), 0.5)), 0.72, 1.1)
    lines = g.smooth_step(crystals, 0.0, 0.06, 1.0, 0.0)
    white = g.math('MAXIMUM', g.math('MULTIPLY', lines, 0.55), cover)
    colour = g.mix(white, tint, frost)
    colour = g.mix(g.smooth_step(g.axis('Z'), 0.0, 2.6, 0.0, 0.3), colour, '#9CCBF0')    # a little bluer towards the top
    rough = g.math('ADD', 0.12, g.math('MULTIPLY', white, 0.5))
    height = g.math('ADD', g.math('MULTIPLY', lines, 0.6), g.math('MULTIPLY', ferns, 0.5))
    return g.finish(colour, rough, 0.0, height, bump=0.45, distance=0.006)


def enamel_sign(name, mask_path, plate, letters, uv_map='bake'):
    """An enamel plate: glossy colour with slightly raised letters taken from a white-on-black mask picture."""
    g = Graph(name)
    img = bpy.data.images.load(mask_path)
    img.colorspace_settings.name = 'Non-Color'
    uv = g.node('ShaderNodeUVMap', uv_map=uv_map)
    tex = g.node('ShaderNodeTexImage', image=img, extension='EXTEND')
    g.link(uv.outputs['UV'], tex.inputs['Vector'])
    mask = tex.outputs['Color']
    m = g.node('ShaderNodeRGBToBW')
    g.link(mask, m.inputs['Color'])
    fac = m.outputs['Val']
    wavy = g.noise(7.0, detail=3.0, rough=0.5)
    colour = g.mix(fac, plate, letters)
    colour = g.mix(g.math('MULTIPLY', wavy, 0.18), colour, '#000000')
    rough = g.math('ADD', 0.14, g.math('MULTIPLY', fac, 0.18))
    height = g.math('ADD', g.math('MULTIPLY', fac, 1.0), g.math('MULTIPLY', wavy, 0.15))
    return g.finish(colour, rough, 0.0, height, bump=0.5, distance=0.004)
