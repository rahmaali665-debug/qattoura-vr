# Shared helpers for the Blender scripts of the VR story.
# Geometry helpers are adapted from ../qattoura-ar/blender/build_models.py; the baking helpers are new.
# Blender axes: X to the right, Z up, the viewer looks along +Y (so the front of a model faces -Y).
import bpy, bmesh, math, os
from mathutils import Vector, Matrix
from mathutils.geometry import tessellate_polygon


# ---------------------------------------------------------------- scene
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = 24
    return sc


def use_cycles(samples=32):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = False
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'OPTIX'
        prefs.get_devices()
        for d in prefs.devices:
            d.use = d.type in ('OPTIX', 'CUDA')
        sc.cycles.device = 'GPU'
    except Exception as e:                    # no GPU: Cycles falls back to the processor
        print('GPU not used:', e)
    return sc


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(hexs):
    """'#RRGGBB' in sRGB to a linear RGBA tuple, which is what Blender nodes expect."""
    hexs = hexs.lstrip('#')
    return tuple(lin(int(hexs[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (1.0,)


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    e.location = loc
    return link(e)


def tree(root):
    out = [root]
    for c in root.children:
        out += tree(c)
    return out


# ---------------------------------------------------------------- meshes
def new_obj(name, me, material=None):
    o = bpy.data.objects.new(name, me)
    if material:
        me.materials.append(material)
    return link(o)


def smooth(me, on=True):
    for p in me.polygons:
        p.use_smooth = on


def auto_sharp(me, angle_deg=38):
    """Smooth shading with hard edges where two faces meet at more than the given angle."""
    limit = math.radians(angle_deg)
    bm = bmesh.new()
    bm.from_mesh(me)
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        e.smooth = not (len(e.link_faces) == 2 and e.calc_face_angle(0.0) > limit)
    bm.to_mesh(me)
    bm.free()


def box(name, size, loc, material, bevel=0.012, rot=(0, 0, 0)):
    """A box with softly bevelled edges. size = (x, y, z)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]; v.co.y *= size[1]; v.co.z *= size[2]
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=min(bevel, min(size) * 0.45), segments=2, affect='EDGES')
    bm.to_mesh(me); bm.free()
    auto_sharp(me)
    o = new_obj(name, me, material)
    o.location = loc; o.rotation_euler = rot
    return o


def cylinder(name, r, depth, loc, material, rot=(0, 0, 0), segments=32, r2=None, bevel=0.0):
    """A cylinder along Z (before rot). r2 gives a cone frustum."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=r, radius2=r if r2 is None else r2, depth=depth)
    if bevel > 0:
        rim = [e for e in bm.edges if len(e.link_faces) == 2 and any(len(f.verts) > 4 for f in e.link_faces)]
        bmesh.ops.bevel(bm, geom=rim, offset=bevel, segments=2, affect='EDGES')
    bm.to_mesh(me); bm.free()
    auto_sharp(me)
    o = new_obj(name, me, material)
    o.location = loc; o.rotation_euler = rot
    return o


def sphere(name, r, loc, material, scale=(1, 1, 1), seg=28, rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(8, seg // 2), radius=r)
    bm.to_mesh(me); bm.free()
    smooth(me)
    o = new_obj(name, me, material)
    o.location = loc; o.scale = scale; o.rotation_euler = rot
    return o


def half_sphere(name, r, loc, material, scale=(1, 1, 1), seg=24):
    """Lower half of a sphere with a flat cap on top (an open mouth)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    top = [v for v in bm.verts if v.co.z > 1e-5]
    bmesh.ops.delete(bm, geom=top, context='VERTS')
    edges = [e for e in bm.edges if e.is_boundary]
    if edges:
        bmesh.ops.holes_fill(bm, edges=edges)
    bm.to_mesh(me); bm.free()
    smooth(me)
    o = new_obj(name, me, material)
    o.location = loc; o.scale = scale
    return o


def torus(name, major, minor, loc, material, rot=(0, 0, 0), seg=40, ring=12):
    """A ring in the XY plane (before rot)."""
    me = bpy.data.meshes.new(name)
    verts, faces = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for j in range(ring):
            b = 2 * math.pi * j / ring
            rr = major + minor * math.cos(b)
            verts.append((rr * math.cos(a), rr * math.sin(a), minor * math.sin(b)))
    for i in range(seg):
        for j in range(ring):
            a, b = i * ring + j, i * ring + (j + 1) % ring
            c, d = ((i + 1) % seg) * ring + (j + 1) % ring, ((i + 1) % seg) * ring + j
            faces.append((a, d, c, b))
    me.from_pydata(verts, [], faces)
    me.update()
    smooth(me)
    o = new_obj(name, me, material)
    o.location = loc; o.rotation_euler = rot
    return o


def tube(name, pts, radii, bevel, material, flatten=None, res=10):
    """A tapered round tube along a smooth path, converted to a mesh."""
    cu = bpy.data.curves.new(name + '_c', 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = bevel
    cu.bevel_resolution = 5
    cu.resolution_u = res
    cu.use_fill_caps = True
    sp = cu.splines.new('NURBS')
    sp.points.add(len(pts) - 1)
    for p, co, rad in zip(sp.points, pts, radii):
        p.co = (co[0], co[1], co[2], 1.0)
        p.radius = rad
    sp.use_endpoint_u = True
    sp.order_u = min(4, len(pts))
    tmp = link(bpy.data.objects.new(name + '_tmp', cu))
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    me.name = name
    smooth(me)
    if flatten:
        for v in me.vertices:
            v.co.x *= flatten[0]; v.co.y *= flatten[1]; v.co.z *= flatten[2]
    return new_obj(name, me, material)


def cone(name, r, depth, material, verts=28):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=0.0, depth=depth)
    bm.to_mesh(me); bm.free()
    auto_sharp(me, 50)
    return new_obj(name, me, material)


def arch_points(width, spring, kind='round', steps=24):
    """Outline of a door opening in the XZ plane, counter-clockwise, starting at the bottom right.
    width: opening width; spring: height where the arch starts; kind: 'round', 'pointed' or 'segment'."""
    w = width / 2
    pts = [(w, 0.0), (w, spring)]
    if kind == 'round':
        for i in range(1, steps):
            a = math.pi * i / steps
            pts.append((w * math.cos(a), spring + w * math.sin(a)))
    elif kind == 'pointed':                    # two arcs, each centred on the opposite spring point
        r = width
        top = math.sqrt(r * r - w * w)
        a_end = math.atan2(top, w)             # the angle at which the two arcs meet above the middle
        for i in range(1, steps):
            a = a_end * i / steps
            pts.append((-w + r * math.cos(a), spring + r * math.sin(a)))
        pts.append((0.0, spring + top))
        for i in range(steps - 1, 0, -1):
            a = a_end * i / steps
            pts.append((w - r * math.cos(a), spring + r * math.sin(a)))
    else:                                      # a shallow arc that rises a quarter of the half-width
        rise = w * 0.28
        r = (w * w + rise * rise) / (2 * rise)
        a0 = math.asin(w / r)
        for i in range(1, steps):
            a = a0 - 2 * a0 * i / steps
            pts.append((r * math.sin(a), spring + rise - r + r * math.cos(a)))
    pts += [(-w, spring), (-w, 0.0)]
    return pts


def arch_top(width, spring, kind):
    return max(z for _, z in arch_points(width, spring, kind))


def extrude_outline(name, outline, y_front, y_back, material, hole=None, bevel=0.0):
    """A flat plate in the XZ plane with the given outline (and an optional hole), extruded from y_front to y_back."""
    loops = [[Vector((x, 0.0, z)) for x, z in outline]]
    if hole:
        loops.append([Vector((x, 0.0, z)) for x, z in hole])
    tris = tessellate_polygon(loops)
    flat = [p for loop in loops for p in loop]
    n = len(flat)
    verts = [(p.x, y_front, p.z) for p in flat] + [(p.x, y_back, p.z) for p in flat]
    faces = []
    for a, b, c in tris:
        faces.append((a, b, c))
        faces.append((c + n, b + n, a + n))
    start = 0
    for loop in loops:
        m = len(loop)
        for i in range(m):
            a, b = start + i, start + (i + 1) % m
            faces.append((a, a + n, b + n, b))
        start += m
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bevel > 0:
        hard = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > math.radians(60)]
        bmesh.ops.bevel(bm, geom=hard, offset=bevel, segments=2, affect='EDGES')
    bm.to_mesh(me); bm.free()
    auto_sharp(me)
    return new_obj(name, me, material)


def apply_transform(o):
    """Bake the object's transform into its mesh."""
    me = o.data
    mirrored = o.matrix_basis.determinant() < 0
    me.transform(o.matrix_basis)
    o.matrix_basis = Matrix.Identity(4)
    if mirrored:
        me.flip_normals()


def join(objs, name):
    for o in objs:
        apply_transform(o)
    with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs, selected_objects=objs):
        bpy.ops.object.join()
    objs[0].name = name
    objs[0].data.name = name
    return objs[0]


def set_origin(o, pivot):
    pivot = Vector(pivot)
    o.data.transform(Matrix.Translation(-pivot))
    o.location = o.location + pivot


def paint(o, hexs):
    """Give every corner of the mesh one colour, stored as the colour attribute 'Color' (COLOR_0 in glTF)."""
    me = o.data
    att = me.color_attributes.get('Color') or me.color_attributes.new('Color', 'BYTE_COLOR', 'CORNER')
    c = rgb(hexs)
    for d in att.data:
        d.color = c


def key(o, path, frame, value):
    setattr(o, path, value)
    o.keyframe_insert(path, frame=frame)


def interp(kind):
    bpy.context.preferences.edit.keyframe_new_interpolation_type = kind


# ---------------------------------------------------------------- baking procedural materials to textures
def new_image(name, width, height, colour=False, fill=(0.5, 0.5, 0.5, 1.0)):
    img = bpy.data.images.new(name, width, height, alpha=False)
    img.generated_color = fill
    img.colorspace_settings.name = 'sRGB' if colour else 'Non-Color'
    return img


def _principled(mat):
    for n in mat.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            return n
    return None


def _output(mat):
    for n in mat.node_tree.nodes:
        if n.type == 'OUTPUT_MATERIAL' and n.is_active_output:
            return n
    return None


def _set_bake_target(objs, image):
    """Every material gets an image node holding the target; Blender bakes into the active image node."""
    for o in objs:
        for slot in o.material_slots:
            nt = slot.material.node_tree
            node = nt.nodes.get('BAKE_TARGET') or nt.nodes.new('ShaderNodeTexImage')
            node.name = 'BAKE_TARGET'
            node.image = image
            for n in nt.nodes:
                n.select = False
            node.select = True
            nt.nodes.active = node


def _bake(objs, kind, image, clear_first=True, margin=8, **kw):
    _set_bake_target(objs, image)
    bpy.ops.object.select_all(action='DESELECT')
    for i, o in enumerate(objs):
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.bake(type=kind, margin=margin, use_clear=clear_first and i == 0, **kw)


def _bake_socket(objs, socket_name, image, margin=8):
    """Bake one input of the Principled BSDF by wiring it into an Emission shader for the duration of the bake."""
    undo = []
    for o in objs:
        for slot in o.material_slots:
            mat = slot.material
            nt = mat.node_tree
            bsdf, out = _principled(mat), _output(mat)
            if bsdf is None or out is None or any(u[0] is mat for u in undo):
                continue
            emit = nt.nodes.new('ShaderNodeEmission')
            sock = bsdf.inputs[socket_name]
            if sock.is_linked:
                nt.links.new(sock.links[0].from_socket, emit.inputs['Color'])
            else:
                v = sock.default_value
                emit.inputs['Color'].default_value = tuple(v) if hasattr(v, '__len__') else (v, v, v, 1.0)
            old = out.inputs['Surface'].links[0].from_socket
            nt.links.new(emit.outputs['Emission'], out.inputs['Surface'])
            undo.append((mat, emit, old, out))
    _bake(objs, 'EMIT', image, margin=margin)
    for mat, emit, old, out in undo:
        mat.node_tree.links.new(old, out.inputs['Surface'])
        mat.node_tree.nodes.remove(emit)


def unwrap_together(objs, margin=0.004):
    """One shared UV layout for several objects, so that they can share one set of textures."""
    for o in objs:
        me = o.data
        layer = me.uv_layers.get('bake') or me.uv_layers.new(name='bake')
        me.uv_layers.active = layer
        layer.active_render = True
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=margin)
    bpy.ops.object.mode_set(mode='OBJECT')


def bake_to_textures(objs, name, work_dir, size=2048, small=1024, ao=0.55, unwrap=True):
    """Replace the procedural materials of the objects with one material that uses baked textures.
    Writes <name>_base.png, <name>_orm.png, <name>_normal.png into work_dir and returns the new material."""
    import numpy as np
    os.makedirs(work_dir, exist_ok=True)
    sc = bpy.context.scene
    use_cycles(8)
    if unwrap:
        unwrap_together(objs)
    w, h = (size, size) if isinstance(size, int) else size
    sw, sh = (small, small) if isinstance(small, int) else small

    base = new_image(name + '_base', w, h, colour=True)
    rough = new_image(name + '_rough', sw, sh)
    metal = new_image(name + '_metal', sw, sh, fill=(0, 0, 0, 1))
    normal = new_image(name + '_normal', sw, sh, fill=(0.5, 0.5, 1.0, 1.0))
    _bake_socket(objs, 'Base Color', base)
    _bake_socket(objs, 'Roughness', rough)
    _bake_socket(objs, 'Metallic', metal)
    sc.cycles.samples = 4
    _bake(objs, 'NORMAL', normal)

    px = np.array(base.pixels[:], dtype=np.float32).reshape(h, w, 4)
    if ao > 0:                                 # soft contact shading in the corners, mixed into the colour
        occ = new_image(name + '_ao', w, h, fill=(1, 1, 1, 1))
        sc.cycles.samples = 48
        _bake(objs, 'AO', occ)
        a = np.array(occ.pixels[:], dtype=np.float32).reshape(h, w, 4)[:, :, 0:1]
        px[:, :, :3] *= (1.0 - ao) + ao * np.clip(a * 1.15, 0.0, 1.0)
        bpy.data.images.remove(occ)
    base.pixels.foreach_set(px.ravel())

    r = np.array(rough.pixels[:], dtype=np.float32).reshape(sh, sw, 4)
    m = np.array(metal.pixels[:], dtype=np.float32).reshape(sh, sw, 4)
    orm = new_image(name + '_orm', sw, sh)
    packed = np.ones((sh, sw, 4), dtype=np.float32)
    packed[:, :, 1] = r[:, :, 0]               # glTF: roughness in green, metallic in blue
    packed[:, :, 2] = m[:, :, 0]
    orm.pixels.foreach_set(packed.ravel())
    bpy.data.images.remove(rough); bpy.data.images.remove(metal)

    for img, suffix in ((base, 'base'), (orm, 'orm'), (normal, 'normal')):
        img.filepath_raw = os.path.join(work_dir, '%s_%s.png' % (name, suffix))
        img.file_format = 'PNG'
        img.save()

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = _principled(mat)
    uv = nt.nodes.new('ShaderNodeUVMap'); uv.uv_map = 'bake'
    t_base = nt.nodes.new('ShaderNodeTexImage'); t_base.image = base
    t_orm = nt.nodes.new('ShaderNodeTexImage'); t_orm.image = orm
    t_nor = nt.nodes.new('ShaderNodeTexImage'); t_nor.image = normal
    for t in (t_base, t_orm, t_nor):
        nt.links.new(uv.outputs['UV'], t.inputs['Vector'])
    sep = nt.nodes.new('ShaderNodeSeparateColor')
    nmap = nt.nodes.new('ShaderNodeNormalMap'); nmap.uv_map = 'bake'
    nt.links.new(t_base.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(t_orm.outputs['Color'], sep.inputs['Color'])
    nt.links.new(sep.outputs['Green'], bsdf.inputs['Roughness'])
    nt.links.new(sep.outputs['Blue'], bsdf.inputs['Metallic'])
    nt.links.new(t_nor.outputs['Color'], nmap.inputs['Color'])
    nt.links.new(nmap.outputs['Normal'], bsdf.inputs['Normal'])
    for o in objs:
        o.data.materials.clear()
        o.data.materials.append(mat)
        for layer in list(o.data.uv_layers):   # only the baked layout is exported
            if layer.name != 'bake':
                o.data.uv_layers.remove(layer)
    return mat


# ---------------------------------------------------------------- export and preview
def export_glb(root, path, frames=1, vertex_colour=False):
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, max(1, frames)
    objs = tree(root)
    for o in sc.objects:
        o.select_set(o in objs)
    bpy.context.view_layer.objects.active = root
    kw = dict(filepath=path, export_format='GLB', use_selection=True, export_apply=True, export_yup=True,
              export_animations=frames > 1, export_image_format='JPEG', export_jpeg_quality=88)
    if frames > 1:
        kw.update(export_animation_mode='SCENE', export_frame_range=True, export_force_sampling=True)
    if vertex_colour:
        kw.update(export_vertex_color='ACTIVE')
    for drop in ((), ('export_jpeg_quality',), ('export_jpeg_quality', 'export_animation_mode'),
                 ('export_jpeg_quality', 'export_animation_mode', 'export_vertex_color')):
        try:
            bpy.ops.export_scene.gltf(**{k: v for k, v in kw.items() if k not in drop})
            break
        except TypeError:
            continue
    print('EXPORTED', os.path.basename(path), os.path.getsize(path), 'bytes')


def render_preview(root, path, res=(900, 1100), view=(2.6, -7.5, 1.7), lens=50, samples=48):
    """A quick Cycles picture of the model under a daylight sky, to check shape and materials by eye."""
    sc = use_cycles(samples)
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = 'PNG'
    try:
        sc.view_settings.view_transform = 'Standard'       # the colours of the textures, not a film look
        sc.view_settings.exposure = -1.7
    except Exception:
        pass
    world = bpy.data.worlds.new('preview_sky'); sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes.get('Background')
    sky = nt.nodes.new('ShaderNodeTexSky')
    try:
        sky.sky_type = 'MULTIPLE_SCATTERING'
        sky.sun_elevation = math.radians(38); sky.sun_rotation = math.radians(-125)
    except Exception:
        pass
    nt.links.new(sky.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = 0.35
    cam = bpy.data.cameras.new('preview_cam'); cam.lens = lens
    co = link(bpy.data.objects.new('preview_cam', cam))
    pts = []
    for o in tree(root):
        if o.type == 'MESH':
            pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    mid = (lo + hi) / 2
    reach = max(hi.x - lo.x, hi.z - lo.z)
    co.location = mid + Vector(view).normalized() * reach * 2.6
    co.rotation_euler = (mid - co.location).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = co
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(co)
    print('PREVIEW', os.path.basename(path))
