"""Resize the downloaded 360-degree photographs for tablets and report where the sun is.

Run:  py -I -X utf8 tools/prepare_env.py <download_dir> <project_dir> [preview_dir]

The photographs are CC0 panoramas from polyhaven.com (tonemapped JPG):
blue_grotto, secluded_beach, kloofendal_48d_partly_cloudy_puresky.
"""
import os
import sys

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
SOURCES = {'hub': 'blue_grotto', 'sea': 'secluded_beach', 'sky': 'kloofendal_48d_partly_cloudy_puresky'}
SIZE = (4096, 2048)
PORTALS = {'sea': (28.0, 12.0), 'sky': (-40.0, 26.0)}       # yaw and pitch of the piece shown inside each door frame


def sun_direction(img):
    """Yaw and pitch (degrees) of the brightest patch. Yaw 0 is the picture centre, positive to the right."""
    small = np.asarray(img.resize((720, 360)).convert('L'), dtype=np.float32)
    blur = np.asarray(Image.fromarray(small.astype(np.uint8)).resize((90, 45)).resize((720, 360)), dtype=np.float32)
    y, x = np.unravel_index(int(np.argmax(blur)), blur.shape)
    return round((x / 720 - 0.5) * 360, 1), round((0.5 - y / 360) * 180, 1)


def main():
    src_dir, out_dir = sys.argv[1], sys.argv[2]
    preview_dir = sys.argv[3] if len(sys.argv) > 3 else None
    os.makedirs(os.path.join(out_dir, 'env'), exist_ok=True)
    for name, asset in SOURCES.items():
        img = Image.open(os.path.join(src_dir, asset, asset + '.jpg')).convert('RGB')
        out = img.resize(SIZE, Image.LANCZOS)
        path = os.path.join(out_dir, 'env', name + '.jpg')
        out.save(path, quality=86, optimize=True, progressive=True)
        print(name, asset, img.size, '->', SIZE, round(os.path.getsize(path) / 1e6, 2), 'MB', 'sun yaw/pitch', sun_direction(out))
        if name in PORTALS:                                  # the view through the open door of this scene
            yaw, pitch = PORTALS[name]
            w, h = out.size
            cw, ch = int(w * 46 / 360), int(h * 84 / 180)
            cx, cy = int((yaw / 360 + 0.5) * w), int((0.5 - pitch / 180) * h)
            view = out.crop((cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2)).resize((512, 936), Image.LANCZOS)
            view.save(os.path.join(out_dir, 'env', 'portal-' + name + '.jpg'), quality=84)
        if preview_dir:
            os.makedirs(preview_dir, exist_ok=True)
            out.resize((1600, 800), Image.LANCZOS).save(os.path.join(preview_dir, name + '_pano.jpg'), quality=80)


if __name__ == '__main__':
    main()
