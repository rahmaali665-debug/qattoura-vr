# Builds the three doors of the VR story and exports them as GLB with baked textures.
# Run:  blender --background --python blender/build_doors.py -- <project_dir> [evaporation] [condensation] [compare]
#
#   door-evaporation.glb   a sun-bleached wooden door in a sandstone arch          nodes: frame, leaf, sign
#   door-condensation.glb  a frosted glass door in a steel pointed arch            nodes: frame, leaf, sign
#   door-compare.glb       a great double door with iron bands and a gold padlock  nodes: frame, leaf_L, leaf_R, lock, sign
#
# Every leaf has its origin on its hinge line, so the scene opens it by turning it about the vertical axis.
# The Arabic words come from blender/text/<door>-sign.png (made by tools/make_text_masks.ps1).
import bpy, bmesh, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (reset, empty, box, cylinder, sphere, torus, cone, extrude_outline, arch_points, arch_top, join,
                    set_origin, new_obj, auto_sharp, bake_to_textures, export_glb, render_preview)
import materials as M

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
PROJECT = os.path.abspath(ARGS[0] if ARGS else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ONLY = ARGS[1:]
MODELS = os.path.join(PROJECT, 'models')
WORK = os.path.join(PROJECT, 'blender', '_work')
TEXT = os.path.join(PROJECT, 'blender', 'text')
os.makedirs(MODELS, exist_ok=True)
os.makedirs(WORK, exist_ok=True)

STEP = 0.24            # height of the two stone steps under every door
SIGN_H = 0.34          # height of the name plate in metres
MASK_H = 384           # height of the mask pictures in pixels


def portal_outline(width, spring, kind, jamb, above):
    """The wall around a door opening: a rectangle with the opening cut out of its lower edge."""
    w, big = width / 2, width / 2 + jamb
    top = arch_top(width, spring, kind) + above
    inner = arch_points(width, spring, kind)                 # starts bottom right, ends bottom left
    return [(big, 0.0), (big, top), (-big, top), (-big, 0.0)] + list(reversed(inner))


def half_outline(width, spring, kind, side):
    """One leaf of a double door: the half of the opening on the given side (+1 right, -1 left)."""
    pts = [(x, z) for x, z in arch_points(width, spring, kind) if x * side > 1e-6]
    mid_top = arch_top(width, spring, kind)
    if side > 0:                                             # points run from bottom right up to the middle
        return pts + [(0.0, mid_top), (0.0, 0.0)]
    return [(0.0, 0.0), (0.0, mid_top)] + pts


def steps(width, depth, mat):
    low = box('step_low', (width + 0.5, depth + 0.5, STEP / 2), (0, 0.05, STEP / 4), mat, bevel=0.02)
    high = box('step_high', (width + 0.12, depth, STEP / 2), (0, 0.05, STEP * 0.75), mat, bevel=0.02)
    return [low, high]


def lift(objs, dz=STEP):
    for o in objs:
        o.location.z += dz


def sign_mesh(name, mask_px_width, centre_x, z, y, title_w):
    """Two plates that share one picture: the name on the left part of the picture, the numeral on the right part.
    The numeral plate hangs to the right of the name, as Arabic reads from right to left."""
    total = mask_px_width + MASK_H
    u_split = mask_px_width / total
    num_w = SIGN_H
    gap = 0.07
    x_title = centre_x - (num_w + gap) / 2
    x_num = x_title + title_w / 2 + gap + num_w / 2
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new('bake')
    depth = 0.02

    def plate(cx, w, u0, u1):
        x0, x1, z0, z1 = cx - w / 2, cx + w / 2, z - SIGN_H / 2, z + SIGN_H / 2
        front = [bm.verts.new((x, y, zz)) for x, zz in ((x0, z0), (x1, z0), (x1, z1), (x0, z1))]
        back = [bm.verts.new((x, y + depth, zz)) for x, zz in ((x0, z0), (x1, z0), (x1, z1), (x0, z1))]
        f = bm.faces.new(front)
        for loop, (u, v) in zip(f.loops, ((u0, 0), (u1, 0), (u1, 1), (u0, 1))):
            loop[uv].uv = (u, v)
        for i in range(4):                                   # the thin sides take the colour of the plate's edge
            j = (i + 1) % 4
            side = bm.faces.new((front[j], front[i], back[i], back[j]))
            for loop in side.loops:
                loop[uv].uv = (u0 + (u1 - u0) * 0.01, 0.01)

    plate(x_title, title_w, 0.0, u_split)
    plate(x_num, num_w, u_split, 1.0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = False
    return new_obj(name, me), total


def finish(name, parts, sign, sign_px, pivots, mats_note=''):
    """Bake, set the hinge origins, parent everything under one root, export and render a preview.
    parts: {node_name: object}; pivots: {node_name: (x, y, z)}"""
    solid = list(parts.values())
    bake_to_textures(solid, 'door-%s' % name, WORK, size=2048, small=1024, ao=0.5)
    bake_to_textures([sign], 'door-%s-sign' % name, WORK, size=(sign_px, MASK_H), small=(sign_px, MASK_H), ao=0.0, unwrap=False)
    root = empty('door-%s' % name)
    for node, o in parts.items():
        o.name = node; o.data.name = node
        if node in pivots:
            set_origin(o, pivots[node])
        o.parent = root
    sign.name = 'sign'; sign.data.name = 'sign'
    sign.parent = root
    bpy.context.view_layer.update()
    export_glb(root, os.path.join(MODELS, 'door-%s.glb' % name))
    render_preview(root, os.path.join(WORK, 'door-%s.png' % name), res=(900, 1100), view=(1.9, -7.5, 0.9), lens=60, samples=64)


# ---------------------------------------------------------------- 1. the evaporation door
def build_evaporation():
    reset()
    width, spring, kind = 1.2, 1.75, 'round'
    stone = M.stone_blocks('sandstone', '#D9B98A', '#B8905F', '#7D6649')
    planks = M.wood('teal_planks', '#B08A5E', '#6B4A2B', plank=0.2, paint='#1E9BA6', wear=0.40)
    iron = M.metal('black_iron', '#3A3632', rough=0.55, dirt='#6B3A1E', brushed=False, hammered=True)
    brass = M.metal('brass', '#E0A93B', rough=0.24)

    portal = extrude_outline('portal', portal_outline(width, spring, kind, 0.34, 0.62), -0.19, 0.19, stone, bevel=0.012)
    sill = box('sill', (width + 0.9, 0.5, 0.06), (0, 0, arch_top(width, spring, kind) + 0.62 + 0.03), stone, bevel=0.012)
    frame = [portal, sill] + steps(width + 0.68, 0.9, stone)

    leaf = [extrude_outline('leaf_wood', arch_points(width - 0.03, spring, kind), -0.03, 0.045, planks, bevel=0.006)]
    for z in (0.42, 1.34):                                   # two strap hinges that reach in from the hinge side
        leaf.append(box('strap', (0.86, 0.022, 0.085), (width / 2 - 0.45, -0.04, z), iron, bevel=0.008))
        leaf.append(cylinder('strap_end', 0.075, 0.022, (width / 2 - 0.88, -0.04, z), iron, rot=(math.radians(90), 0, 0), bevel=0.006))
        for dx in (0.12, 0.42, 0.72):
            leaf.append(sphere('nail', 0.022, (width / 2 - dx, -0.052, z), iron, scale=(1, 0.6, 1), seg=12))
    # ring handle on the side away from the hinges
    leaf.append(cylinder('handle_plate', 0.075, 0.016, (-width / 2 + 0.2, -0.038, 1.02), iron, rot=(math.radians(90), 0, 0), bevel=0.005))
    leaf.append(torus('handle_ring', 0.085, 0.014, (-width / 2 + 0.2, -0.062, 0.955), brass, rot=(math.radians(90), 0, 0)))
    # the sun emblem: a brass disc with twelve rays
    sun_z = 1.86
    leaf.append(cylinder('sun_disc', 0.17, 0.035, (0, -0.045, sun_z), brass, rot=(math.radians(90), 0, 0), segments=40, bevel=0.01))
    leaf.append(sphere('sun_dome', 0.12, (0, -0.058, sun_z), brass, scale=(1, 0.3, 1), seg=24))
    for i in range(12):
        a = 2 * math.pi * i / 12
        ray = cone('sun_ray', 0.034, 0.15 if i % 2 == 0 else 0.1, brass, verts=4)
        ray.scale = (1, 0.4, 1)
        ray.rotation_euler = (0, a, 0)                      # the cone points along +Z; turn it about Y so it points outwards
        reach = 0.17 + (0.075 if i % 2 == 0 else 0.05)
        ray.location = (math.sin(a) * reach, -0.045, sun_z + math.cos(a) * reach)
        leaf.append(ray)

    lift(frame[:2]); lift(leaf)
    sign, sign_px = sign_mesh('sign', 1024, 0.0, arch_top(width, spring, kind) + STEP + 0.33, -0.205, 0.9)
    sign.data.materials.append(M.enamel_sign('sign_evaporation', os.path.join(TEXT, 'evaporation-sign.png'), '#C8471C', '#FFF3D6'))
    parts = {'frame': join(frame, 'frame'), 'leaf': join(leaf, 'leaf')}
    finish('evaporation', parts, sign, sign_px, {'leaf': (width / 2 - 0.015, 0.0, 0.0)})


# ---------------------------------------------------------------- 2. the condensation door
def build_condensation():
    reset()
    width, spring, kind = 1.15, 1.6, 'pointed'
    steel = M.metal('brushed_steel', '#C9CED4', rough=0.3)
    chrome = M.metal('chrome', '#E8ECF0', rough=0.12, brushed=False)
    glass = M.frosted_glass('frost', tint='#6FAEE0', frost='#F4FAFF')
    marble = M.granite('ice_marble', '#D5E3F0', '#FFFFFF', '#9DB5CF', rough=0.3)
    white = M.plain('white_enamel', '#F2F7FC', rough=0.32)

    portal = extrude_outline('portal', portal_outline(width, spring, kind, 0.2, 0.58), -0.15, 0.15, marble, bevel=0.012)
    band = arch_points(width + 0.16, spring, kind) + list(reversed(arch_points(width + 0.02, spring, kind)))   # a bright band that follows the arch
    trim = extrude_outline('trim', band, -0.175, -0.15, chrome, bevel=0.006)
    frame = [portal, trim] + steps(width + 0.4, 0.8, marble)

    inner = [(x * 0.84, 0.1 + z * 0.9) for x, z in arch_points(width - 0.03, spring, kind)]
    leaf = [extrude_outline('leaf_frame', arch_points(width - 0.03, spring, kind), -0.03, 0.03, steel, hole=inner, bevel=0.006),
            extrude_outline('leaf_glass', [(x * 1.02, z + 0.0) for x, z in inner], -0.012, 0.012, glass)]
    # a tall bar handle on the side away from the hinges
    hx = -width / 2 + 0.17
    leaf.append(cylinder('bar', 0.02, 0.9, (hx, -0.085, 1.12), chrome, bevel=0.004))
    for z in (0.78, 1.46):
        leaf.append(cylinder('standoff', 0.013, 0.07, (hx, -0.05, z), chrome, rot=(math.radians(90), 0, 0)))
    # the cloud emblem: overlapping steel discs on a flat base
    cz = 1.72
    for dx, dz, r in ((0.0, 0.05, 0.13), (-0.13, 0.0, 0.095), (0.14, 0.01, 0.1), (-0.22, -0.035, 0.065), (0.23, -0.03, 0.068)):
        leaf.append(cylinder('cloud_disc', r, 0.03, (dx, -0.03, cz + dz), white, rot=(math.radians(90), 0, 0), segments=36, bevel=0.008))
    leaf.append(box('cloud_base', (0.46, 0.03, 0.07), (0.005, -0.03, cz - 0.07), white, bevel=0.012))
    # three snow crystals under the cloud
    for dx, dz in ((-0.14, -0.26), (0.0, -0.33), (0.14, -0.26)):
        for k in range(3):
            leaf.append(box('crystal', (0.12, 0.01, 0.018), (dx, -0.02, cz + dz), white, bevel=0.003, rot=(0, k * math.pi / 3, 0)))

    lift(frame[:2]); lift(leaf)
    sign, sign_px = sign_mesh('sign', 1024, 0.0, arch_top(width, spring, kind) + STEP + 0.31, -0.165, 0.9)
    sign.data.materials.append(M.enamel_sign('sign_condensation', os.path.join(TEXT, 'condensation-sign.png'), '#1C5FB8', '#FFFFFF'))
    parts = {'frame': join(frame, 'frame'), 'leaf': join(leaf, 'leaf')}
    finish('condensation', parts, sign, sign_px, {'leaf': (width / 2 - 0.015, 0.0, 0.0)})


# ---------------------------------------------------------------- 3. the comparison door
def build_compare():
    reset()
    width, spring, kind = 2.1, 2.25, 'segment'
    stone = M.granite('granite', '#5A5D64', '#8E929A', '#2B2D31', rough=0.5)
    walnut = M.wood('walnut', '#6E4526', '#33200F', plank=0.26)
    iron = M.metal('wrought_iron', '#2E2C2A', rough=0.5, dirt='#4A2E1C', brushed=False, hammered=True)
    gold = M.metal('gold', '#F2C141', rough=0.2)

    top = arch_top(width, spring, kind)
    portal = extrude_outline('portal', portal_outline(width, spring, kind, 0.44, 0.66), -0.24, 0.24, stone, bevel=0.014)
    cornice = box('cornice', (width + 1.2, 0.62, 0.1), (0, 0, top + 0.66 + 0.05), stone, bevel=0.02)
    keystone = extrude_outline('keystone', [(-0.14, top - 0.04), (0.14, top - 0.04), (0.2, top + 0.36), (-0.2, top + 0.36)],
                               -0.29, -0.2, stone, bevel=0.01)
    bases = [box('base', (0.56, 0.6, 0.3), (s * (width / 2 + 0.22), 0, 0.15), stone, bevel=0.02) for s in (-1, 1)]
    frame = [portal, cornice, keystone] + bases + steps(width + 0.9, 1.0, stone)

    leaves = {}
    for side, node in ((1, 'leaf_R'), (-1, 'leaf_L')):
        gapped = [(side * 0.004 if abs(x) < 1e-6 else x, z) for x, z in half_outline(width - 0.03, spring, kind, side)]   # a hair of space between the leaves
        bits = [extrude_outline(node + '_wood', gapped, -0.04, 0.05, walnut, bevel=0.006)]
        mid = side * width / 4
        for z in (0.45, 1.3, 2.05):                          # iron bands with a row of studs
            bits.append(box('band', (width / 2 - 0.07, 0.02, 0.1), (mid, -0.05, z), iron, bevel=0.008))
            for k in range(5):
                bits.append(sphere('stud', 0.026, (side * (0.12 + k * 0.2), -0.062, z), iron, scale=(1, 0.6, 1), seg=12))
        # the ring that the padlock holds, and one ring of the Venn emblem
        bits.append(torus('lock_ring', 0.06, 0.013, (side * 0.085, -0.066, 1.02), iron, rot=(0, math.radians(90), 0), seg=24, ring=10))
        bits.append(cylinder('ring_plate', 0.05, 0.014, (side * 0.15, -0.05, 1.02), iron, rot=(math.radians(90), 0, 0), bevel=0.004))
        bits.append(torus('venn', 0.3, 0.022, (side * 0.17, -0.055 - (0.012 if side > 0 else 0.0), 1.68), gold, rot=(math.radians(90), 0, 0), seg=56))
        leaves[node] = bits

    lock = [box('lock_body', (0.25, 0.085, 0.2), (0, -0.12, 0.86), gold, bevel=0.022),
            cylinder('keyhole', 0.022, 0.012, (0, -0.166, 0.88), iron, rot=(math.radians(90), 0, 0)),
            box('keyslot', (0.016, 0.012, 0.06), (0, -0.166, 0.84), iron, bevel=0.003)]
    shackle = torus('shackle', 0.085, 0.017, (0, -0.12, 0.985), gold, rot=(math.radians(90), 0, 0), seg=32, ring=10)
    lock.append(shackle)

    lift(frame[:5]); lift(lock)
    for bits in leaves.values():
        lift(bits)
    sign, sign_px = sign_mesh('sign', 1536, 0.0, top + STEP + 0.4, -0.305, 1.36)
    sign.data.materials.append(M.enamel_sign('sign_compare', os.path.join(TEXT, 'compare-sign.png'), '#17382B', '#F5D36B'))
    parts = {'frame': join(frame, 'frame'), 'leaf_R': join(leaves['leaf_R'], 'leaf_R'),
             'leaf_L': join(leaves['leaf_L'], 'leaf_L'), 'lock': join(lock, 'lock')}
    half = width / 2 - 0.015
    finish('compare', parts, sign, sign_px,
           {'leaf_R': (half, 0.0, 0.0), 'leaf_L': (-half, 0.0, 0.0), 'lock': (0.0, -0.12, 0.86 + STEP)})


JOBS = {'evaporation': build_evaporation, 'condensation': build_condensation, 'compare': build_compare}

if __name__ == '__main__':
    for job, fn in JOBS.items():
        if ONLY and job not in ONLY:
            continue
        fn()
        print('DOOR DONE', job)
    print('ALL DOORS DONE')
