# Builds the small models of the VR story: the two arrows and the two drop characters.
# Run:  blender --background --python blender/build_props.py -- <project_dir> [name ...]
#   names: arrow-heat, arrow-up, drop, drop-sad (default: all)
# Every model uses one material that takes its colour from the vertices, so each mesh is a single draw call.
import bpy, bmesh, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (reset, rgb, empty, new_obj, smooth, sphere, half_sphere, tube, cone, join, set_origin, paint,
                    key, interp, export_glb, render_preview)

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
PROJECT = os.path.abspath(ARGS[0] if ARGS else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ONLY = ARGS[1:]
MODELS = os.path.join(PROJECT, 'models')
WORK = os.path.join(PROJECT, 'blender', '_work')
os.makedirs(MODELS, exist_ok=True)
os.makedirs(WORK, exist_ok=True)


def vertex_material(name, rough=0.22):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get('Principled BSDF')
    att = nt.nodes.new('ShaderNodeVertexColor')
    att.layer_name = 'Color'
    nt.links.new(att.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = 0.0
    return m


def paint_gradient(o, stops):
    """Colour the mesh along Z. stops: [(z, '#RRGGBB'), ...] in rising order."""
    me = o.data
    att = me.color_attributes.get('Color') or me.color_attributes.new('Color', 'BYTE_COLOR', 'CORNER')
    cols = [(z, rgb(c)) for z, c in stops]
    for poly in me.polygons:
        for li in poly.loop_indices:
            z = me.vertices[me.loops[li].vertex_index].co.z
            if z <= cols[0][0]:
                c = cols[0][1]
            elif z >= cols[-1][0]:
                c = cols[-1][1]
            else:
                for (z0, c0), (z1, c1) in zip(cols, cols[1:]):
                    if z0 <= z <= z1:
                        t = (z - z0) / (z1 - z0)
                        c = tuple(a + (b - a) * t for a, b in zip(c0, c1))
                        break
            att.data[li].color = c


# ---------------------------------------------------------------- arrows
# Both arrows are 1 unit long, from the origin to +Z (which is +Y, up, in the exported GLB). The scene turns and scales them.
def build_arrow(name, path, radii, bevel, head_r, head_len, stops):
    reset()
    root = empty(name)
    m = vertex_material(name, rough=0.18)
    shaft = tube(name + '_shaft', path, radii, bevel, m, res=14)
    head = cone(name + '_head', head_r, head_len, m, verts=32)
    head.location = (0, 0, 1.0 - head_len / 2)
    a = join([shaft, head], 'arrow')
    smooth(a.data)
    paint_gradient(a, stops)
    a.parent = root
    return root, 1


def build_arrow_heat():
    # a heat wave: the shaft swings from side to side, yellow at the sun end, red at the tip
    path = [(0.0, 0, 0.0), (0.085, 0, 0.16), (-0.085, 0, 0.36), (0.075, 0, 0.56), (0.0, 0, 0.72), (0.0, 0, 0.76)]
    return build_arrow('arrow-heat', path, [0.55, 0.8, 0.95, 1.0, 1.0, 1.0], 0.05, 0.125, 0.27,
                       [(0.0, '#FFE14A'), (0.4, '#FF9A12'), (0.78, '#FF3B14'), (1.0, '#E01208')])


def build_arrow_up():
    # rising water vapour: a calm, nearly straight arrow, deep blue below, almost white at the tip
    path = [(0.0, 0, 0.0), (0.035, 0, 0.25), (-0.03, 0, 0.5), (0.0, 0, 0.72), (0.0, 0, 0.77)]
    return build_arrow('arrow-up', path, [0.5, 0.8, 0.95, 1.0, 1.0], 0.045, 0.115, 0.25,
                       [(0.0, '#1F6FE0'), (0.5, '#4FB4FF'), (0.8, '#BFE9FF'), (1.0, '#F2FBFF')])


# ---------------------------------------------------------------- the drop character
def teardrop_mesh(name, w=0.62, top=1.3, bottom=0.78, lean=0.2, rings=44, segs=40):
    verts, faces = [], []
    for i in range(rings + 1):
        th = math.pi * i / rings
        r = w * math.sin(th) * (math.sin(th / 2) ** 0.85) * 1.32
        c = math.cos(th)
        z = top * c if c > 0 else bottom * c
        off = lean * (max(z, 0) / top) ** 2
        for j in range(segs):
            a = 2 * math.pi * j / segs
            verts.append((off + r * math.cos(a), r * math.sin(a), z))
    for i in range(rings):
        for j in range(segs):
            a = i * segs + j; b = i * segs + (j + 1) % segs
            faces.append((a, b, b + segs, a + segs))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate(); me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    smooth(me)
    return me


def face(m, sad, cx=0.02, cz=0.06, y=-0.60, eye_dx=0.23, eye_r=0.185, mouth_z=-0.28, mouth_r=0.2,
         cheek_dx=0.45, cheek_z=-0.17, cheek_r=0.12):
    """Cartoon face on the -Y side. The sad face has worried brows, a frown and a drop of sweat."""
    def part(o, colour):
        paint(o, colour)
        return o

    parts = []
    for s in (-1, 1):
        ex = cx + s * eye_dx
        parts.append(part(sphere('eye', eye_r, (ex, y, cz), m, scale=(1, 0.45, 1.15)), '#FFFFFF'))
        parts.append(part(sphere('iris', eye_r * 0.68, (ex + 0.02 * s, y - eye_r * 0.3, cz - 0.01), m, scale=(1, 0.4, 1.1)), '#1B63D6'))
        parts.append(part(sphere('pupil', eye_r * 0.4, (ex + 0.02 * s, y - eye_r * 0.42, cz - 0.01), m, scale=(1, 0.4, 1.1)), '#081A3A'))
        parts.append(part(sphere('glint', eye_r * 0.2, (ex - 0.045, y - eye_r * 0.52, cz + eye_r * 0.33), m, scale=(1, 0.4, 1)), '#FFFFFF'))
        brow = tube('brow', [(-eye_r * 0.7, 0, 0), (0, 0, eye_r * 0.28), (eye_r * 0.7, 0, 0.02)], [0.7, 1, 0.5], eye_r * 0.13, m)
        brow.location = (ex, y + 0.02, cz + eye_r * 1.55)
        brow.rotation_euler = (0, math.radians((20 if sad else -10) * s), 0)
        parts.append(part(brow, '#0C57B8'))
        parts.append(part(sphere('cheek', cheek_r, (cx + s * cheek_dx, y + 0.04, cheek_z), m, scale=(1, 0.25, 0.75)),
                          '#FF6F7F' if sad else '#FF8F9C'))
    if sad:
        mouth = half_sphere('mouth', mouth_r * 0.8, (cx, y + 0.02, mouth_z - 0.1), m, scale=(1, 0.45, 0.8))
        mouth.rotation_euler = (0, math.pi, 0)          # turned over: flat side down, a frown
        parts.append(part(mouth, '#8F1023'))
        parts.append(part(sphere('sweat', 0.075, (0.47, -0.42, 0.62), m, scale=(0.75, 0.6, 1.25), rot=(0, math.radians(-18), 0)), '#CFEFFF'))
    else:
        parts.append(part(half_sphere('mouth', mouth_r, (cx, y + 0.02, mouth_z), m, scale=(1, 0.45, 1.05)), '#B3122B'))
        parts.append(part(sphere('tongue', mouth_r * 0.55, (cx, y - 0.01, mouth_z - mouth_r * 0.62), m, scale=(1.1, 0.4, 0.6)), '#FF6F86'))
    return parts


def build_drop(sad=False):
    reset()
    root = empty('Drop')
    m = vertex_material('drop', rough=0.16)
    blue, dark = '#2AA9FF', '#1688F0'
    body = new_obj('drop_body', teardrop_mesh('drop_body'), m)
    paint(body, blue)
    shine = sphere('shine', 0.15, (-0.26, -0.36, 0.46), m, scale=(0.5, 0.22, 1.15), rot=(0, math.radians(-25), 0))
    paint(shine, '#E9F8FF')
    parts = [body, shine] + face(m, sad)
    for s in (-1, 1):
        leg = tube('leg', [(s * 0.2, 0, -0.6), (s * 0.24, 0, -0.82), (s * 0.27, 0, -1.0)], [1, 0.9, 0.85], 0.1, m)
        paint(leg, dark)
        foot = sphere('foot', 0.17, (s * 0.3, -0.06, -1.06), m, scale=(1, 1.3, 0.72))
        paint(foot, dark)
        parts += [leg, foot]
    body = join(parts, 'drop_body')
    body.parent = root

    arms = []
    for s, nm in ((-1, 'arm_R'), (1, 'arm_L')):
        sh = (s * 0.5, 0, -0.05)
        # the sad drop lets her arms hang; the happy one holds them up
        hand = (s * 0.86, 0, -0.52) if sad else (s * 1.0, 0, 0.5)
        mid = [(s * 0.72, 0, -0.16), (s * 0.82, 0, -0.34)] if sad else [(s * 0.74, 0, 0.1), (s * 0.9, 0, 0.32)]
        bits = [tube(nm, [sh] + mid + [hand], [1.1, 0.95, 0.85, 0.85], 0.1, m),
                sphere('palm', 0.15, hand, m, scale=(1, 0.75, 1.05))]
        up = -1 if sad else 1
        for dx, dz in ((0.13, 0.12), (0.03, 0.2), (-0.09, 0.16)):
            bits.append(sphere('finger', 0.075, (hand[0] + s * dx, 0, hand[2] + up * dz), m, scale=(0.85, 0.8, 1.25)))
        for b in bits:
            paint(b, blue)
        arm = join(bits, nm)
        set_origin(arm, sh)
        arm.parent = root
        arms.append((arm, s))

    interp('BEZIER')
    lift = 0.06 if sad else 0.12              # the sad drop bounces less
    for f, z, sx, sz in ((1, 0, 1, 1), (9, lift, 0.96, 1.06), (17, 0, 1.05, 0.94), (25, 0, 1, 1),
                         (33, lift, 0.96, 1.06), (41, 0, 1.05, 0.94), (49, 0, 1, 1)):
        key(body, 'location', f, (0, 0, z))
        key(body, 'scale', f, (sx, sx, sz))
    swing = 8 if sad else 22
    for arm, s in arms:
        base = arm.location.copy()
        for f, ang, z in ((1, 0, 0), (7, swing, 0.1), (13, -8, 0.04), (19, swing, 0.02), (25, 0, 0),
                          (31, swing, 0.1), (37, -8, 0.04), (43, swing, 0.02), (49, 0, 0)):
            key(arm, 'rotation_euler', f, (0, math.radians(-ang * s), 0))
            key(arm, 'location', f, (base.x, base.y, base.z + z * (0.5 if sad else 1)))
    return root, 48


JOBS = [('arrow-heat', build_arrow_heat, (700, 900)), ('arrow-up', build_arrow_up, (700, 900)),
        ('drop', lambda: build_drop(False), (800, 900)), ('drop-sad', lambda: build_drop(True), (800, 900))]


def main():
    for name, fn, res in JOBS:
        if ONLY and name not in ONLY:
            continue
        root, frames = fn()
        bpy.context.view_layer.update()
        export_glb(root, os.path.join(MODELS, name + '.glb'), frames, vertex_colour=True)
        bpy.context.scene.frame_set(1)
        render_preview(root, os.path.join(WORK, name + '.png'), res=res, view=(1.6, -7.5, 1.2))
    print('PROPS DONE')


if __name__ == '__main__':
    main()
