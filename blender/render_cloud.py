# Renders the realistic cloud of the sky scene: a volumetric cumulus in Cycles, as four growing stages.
# Run:  blender --background --python blender/render_cloud.py -- <project_dir> [scale]
#   scale: 1.0 for the final pictures (default), 0.5 for a quick test.
# Output: textures/cloud-1.png ... cloud-4.png (RGBA, same camera, so the stages can be cross-faded in the scene).
import bpy, math, os, sys
from mathutils import Vector

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
PROJECT = os.path.abspath(ARGS[0] if ARGS else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCALE = float(ARGS[1]) if len(ARGS) > 1 else 1.0
OUT = os.path.join(PROJECT, 'textures')
os.makedirs(OUT, exist_ok=True)

# Puffs of the cloud: x (right), y (depth), z (up), radius. The first ones are the core; later ones make it grow.
PUFFS = [
    # the core: a wide flat-bottomed heap
    (-0.20, 0.00, 0.45, 1.05), (-1.30, 0.10, 0.35, 0.95), (0.90, -0.05, 0.40, 1.00),
    # second stage: the heap spreads and gets its first domes
    (1.90, 0.05, 0.25, 0.80), (-2.30, 0.00, 0.20, 0.75), (-0.50, -0.10, 1.35, 0.90), (0.60, 0.10, 1.20, 0.80),
    # third stage: a tower grows left of the middle
    (-1.50, 0.00, 1.15, 0.75), (1.50, 0.00, 0.95, 0.60), (-0.80, 0.00, 2.05, 0.65), (0.35, 0.00, 1.85, 0.55),
    (2.70, 0.00, 0.10, 0.55),
    # full cloud: top, wings and the bulges that face the viewer
    (-0.10, 0.05, 2.35, 0.58), (-3.00, 0.00, 0.08, 0.50), (2.20, 0.10, 0.75, 0.45), (-2.20, 0.00, 0.75, 0.50),
    (-1.20, -0.45, 0.25, 0.80), (0.40, -0.50, 0.20, 0.85), (1.20, -0.40, 0.60, 0.50), (-0.30, -0.45, 1.00, 0.60),
]
STAGES = [3, 7, 12, len(PUFFS)]
BASE_Z = -0.25                                # the flat underside of the cloud


def use_gpu(scene):
    scene.render.engine = 'CYCLES'
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'OPTIX'
        prefs.get_devices()
        for d in prefs.devices:
            d.use = d.type in ('OPTIX', 'CUDA')
        scene.cycles.device = 'GPU'
    except Exception as e:                    # no GPU: Cycles falls back to the processor
        print('GPU not used:', e)


def cloud_material():
    m = bpy.data.materials.new('cloud_volume')
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    N, L = nt.nodes.new, nt.links.new
    out = N('ShaderNodeOutputMaterial')
    vol = N('ShaderNodeVolumePrincipled')
    vol.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    vol.inputs['Anisotropy'].default_value = 0.72
    L(vol.outputs['Volume'], out.inputs['Volume'])

    coord = N('ShaderNodeTexCoord')           # Object: 0 at the puff centre, 1 at its surface
    geo = N('ShaderNodeNewGeometry')          # Position: world space, so the noise is continuous across puffs
    dist = N('ShaderNodeVectorMath'); dist.operation = 'LENGTH'
    L(coord.outputs['Object'], dist.inputs[0])

    big = N('ShaderNodeTexNoise'); big.inputs['Scale'].default_value = 1.55
    big.inputs['Detail'].default_value = 7.0; big.inputs['Roughness'].default_value = 0.62
    L(geo.outputs['Position'], big.inputs['Vector'])
    fine = N('ShaderNodeTexNoise'); fine.inputs['Scale'].default_value = 6.5
    fine.inputs['Detail'].default_value = 5.0; fine.inputs['Roughness'].default_value = 0.7
    L(geo.outputs['Position'], fine.inputs['Vector'])

    def math_node(op, a, b=None, value=None):
        n = N('ShaderNodeMath'); n.operation = op
        L(a, n.inputs[0])
        if b is not None:
            L(b, n.inputs[1])
        if value is not None:
            n.inputs[1].default_value = value
        return n.outputs[0]

    # the puff edge is pushed in and out by noise; the round cells of the Voronoi texture give the cauliflower billows
    cells = N('ShaderNodeTexVoronoi'); cells.inputs['Scale'].default_value = 2.3
    L(geo.outputs['Position'], cells.inputs['Vector'])
    wob = math_node('MULTIPLY', math_node('SUBTRACT', big.outputs['Fac'], value=0.5), value=1.0)
    wob2 = math_node('MULTIPLY', math_node('SUBTRACT', fine.outputs['Fac'], value=0.5), value=0.3)
    wob3 = math_node('MULTIPLY', math_node('SUBTRACT', cells.outputs['Distance'], value=0.32), value=0.75)
    shape = math_node('ADD', math_node('ADD', math_node('ADD', dist.outputs['Value'], wob), wob2), wob3)

    fall = N('ShaderNodeMapRange'); fall.interpolation_type = 'SMOOTHSTEP'
    fall.inputs['From Min'].default_value = 0.76; fall.inputs['From Max'].default_value = 1.0
    fall.inputs['To Min'].default_value = 1.0; fall.inputs['To Max'].default_value = 0.0
    L(shape, fall.inputs['Value'])

    # nearly flat base: nothing below BASE_Z, full density a little above it; noise keeps the underside from being a ruler line
    sep = N('ShaderNodeSeparateXYZ'); L(geo.outputs['Position'], sep.inputs[0])
    lifted = math_node('ADD', sep.outputs['Z'], math_node('MULTIPLY', math_node('SUBTRACT', big.outputs['Fac'], value=0.5), value=0.55))
    base = N('ShaderNodeMapRange'); base.interpolation_type = 'SMOOTHSTEP'
    base.inputs['From Min'].default_value = BASE_Z; base.inputs['From Max'].default_value = BASE_Z + 0.6
    L(lifted, base.inputs['Value'])

    dens = math_node('MULTIPLY', math_node('MULTIPLY', fall.outputs['Result'], base.outputs['Result']), value=9.0)
    L(dens, vol.inputs['Density'])
    return m


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    use_gpu(sc)
    sc.cycles.samples = 128 if SCALE >= 1 else 96
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 48
    sc.cycles.volume_bounces = 40
    sc.cycles.transparent_max_bounces = 16
    try:
        sc.cycles.volume_step_rate = 0.6
    except Exception:
        pass
    sc.render.film_transparent = True
    sc.render.resolution_x = int(1536 * SCALE)
    sc.render.resolution_y = int(1024 * SCALE)
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.image_settings.compression = 80
    for name in ('Standard', 'Filmic', 'AgX'):
        try:
            sc.view_settings.view_transform = name
            break
        except Exception:
            continue
    sc.view_settings.exposure = 0.0

    world = bpy.data.worlds.new('sky'); sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    bg.inputs[0].default_value = (0.62, 0.76, 1.0, 1.0)      # blue sky light fills the shaded side
    bg.inputs[1].default_value = 0.7

    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.4; sun.angle = math.radians(4)
    so = bpy.data.objects.new('sun', sun); sc.collection.objects.link(so)
    toward = Vector((0.5, -0.6, 0.66)).normalized()        # from the cloud towards the sun: upper right, a little in front
    so.rotation_euler = toward.to_track_quat('Z', 'Y').to_euler()

    cam = bpy.data.cameras.new('cam'); cam.lens = 70
    co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co)
    co.location = (0.0, -19.5, 0.3)
    look = Vector((0.0, 0.0, 1.05))
    co.rotation_euler = (look - co.location).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = co

    mat = cloud_material()
    mesh = bpy.data.meshes.new('puff')
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    bm.to_mesh(mesh); bm.free()
    mesh.materials.append(mat)
    puffs = []
    for i, (x, y, z, r) in enumerate(PUFFS):
        o = bpy.data.objects.new('puff_%02d' % i, mesh)
        o.location = (x, y, z)
        o.scale = (r * 1.25, r * 1.1, r * 1.12)              # room for the noisy edge inside the mesh
        sc.collection.objects.link(o)
        puffs.append(o)
    return sc, puffs


def main():
    sc, puffs = build()
    only = [int(a) for a in ARGS[2:]] if len(ARGS) > 2 else None
    for stage, count in enumerate(STAGES, start=1):
        if only and stage not in only:
            continue
        for i, o in enumerate(puffs):
            o.hide_render = i >= count
        sc.render.filepath = os.path.join(OUT, 'cloud-%d.png' % stage)
        bpy.ops.render.render(write_still=True)
        print('RENDERED cloud stage', stage, 'puffs', count)
    print('CLOUD DONE')


if __name__ == '__main__':
    main()
