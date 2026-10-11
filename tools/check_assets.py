"""Checks the generated files of the VR story: models, cloud pictures, photographs and total size.

Run from the project folder:  py -I -X utf8 tools/check_assets.py
Exit code 0 means every check passed.
"""
import json
import os
import struct
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS = {
    'door-evaporation.glb': {'nodes': ['frame', 'leaf', 'sign']},
    'door-condensation.glb': {'nodes': ['frame', 'leaf', 'sign']},
    'door-compare.glb': {'nodes': ['frame', 'leaf_L', 'leaf_R', 'lock', 'sign']},
    'arrow-heat.glb': {'nodes': ['arrow'], 'materials': 1, 'vertex_colour': True},
    'arrow-up.glb': {'nodes': ['arrow'], 'materials': 1, 'vertex_colour': True},
    'drop.glb': {'nodes': ['drop_body', 'arm_L', 'arm_R'], 'materials': 1, 'vertex_colour': True, 'animated': True},
    'drop-sad.glb': {'nodes': ['drop_body', 'arm_L', 'arm_R'], 'materials': 1, 'vertex_colour': True, 'animated': True},
}
CLOUDS = ['cloud-%d.png' % n for n in (1, 2, 3, 4)]
PHOTOS = ['hub.jpg', 'sea.jpg', 'sky.jpg']
SKIP = {'.git', '_work', '__pycache__'}
LIMIT_MB = 25
problems = []


def check(ok, message):
    print(('ok    ' if ok else 'FAIL  ') + message)
    if not ok:
        problems.append(message)


def read_glb(path):
    with open(path, 'rb') as f:
        data = f.read()
    magic, _version, _length = struct.unpack('<III', data[:12])
    if magic != 0x46546C67:
        raise ValueError('not a GLB file')
    size, kind = struct.unpack('<II', data[12:20])
    if kind != 0x4E4F534A:
        raise ValueError('first chunk is not JSON')
    return json.loads(data[20:20 + size])


for name, want in MODELS.items():
    path = os.path.join(ROOT, 'models', name)
    if not os.path.isfile(path):
        check(False, 'models/%s is missing' % name)
        continue
    gltf = read_glb(path)
    names = [n.get('name') for n in gltf.get('nodes', [])]
    missing = [n for n in want['nodes'] if n not in names]
    check(not missing, 'models/%s has nodes %s' % (name, ', '.join(want['nodes'])) + (' (missing: %s)' % missing if missing else ''))
    if 'materials' in want:
        count = len(gltf.get('materials', []))
        check(count == want['materials'], 'models/%s has %d material(s)' % (name, count))
    if want.get('vertex_colour'):
        coloured = all('COLOR_0' in p['attributes'] for m in gltf['meshes'] for p in m['primitives'])
        check(coloured, 'models/%s carries vertex colours on every mesh' % name)
    if want.get('animated'):
        check(len(gltf.get('animations', [])) > 0, 'models/%s has an animation' % name)
    if name.startswith('door-'):
        check(len(gltf.get('images', [])) >= 4, 'models/%s has baked textures (%d images)' % (name, len(gltf.get('images', []))))

for name in CLOUDS:
    path = os.path.join(ROOT, 'textures', name)
    if not os.path.isfile(path):
        check(False, 'textures/%s is missing' % name)
        continue
    im = Image.open(path)
    lo, hi = im.getchannel('A').getextrema() if im.mode == 'RGBA' else (255, 255)
    check(im.mode == 'RGBA' and lo == 0 and hi > 200, 'textures/%s is RGBA with a transparent background (%dx%d)' % ((name,) + im.size))

for name in PHOTOS:
    path = os.path.join(ROOT, 'env', name)
    if not os.path.isfile(path):
        check(False, 'env/%s is missing' % name)
        continue
    check(Image.open(path).size == (4096, 2048), 'env/%s is 4096x2048' % name)
for name in ('portal-sea.jpg', 'portal-sky.jpg'):
    check(os.path.isfile(os.path.join(ROOT, 'env', name)), 'env/%s exists' % name)

total = 0
for folder, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP]
    total += sum(os.path.getsize(os.path.join(folder, f)) for f in files)
check(total < LIMIT_MB * 1e6, 'folder size %.1f MB is under %d MB (without .git and blender/_work)' % (total / 1e6, LIMIT_MB))

print('\n%d problem(s)' % len(problems))
sys.exit(1 if problems else 0)
