"""Paste a transparent render over a piece of an environment photograph, to judge how it will look in the scene.

Run:  py -I -X utf8 tools/preview_over_photo.py <render.png> <env.jpg> <out.jpg> [yaw_deg] [pitch_deg] [width_px]
The photograph is cropped around the given direction (default: yaw 0, pitch +15) to a 3:2 window.
"""
import sys

from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def main():
    render, env, out = sys.argv[1:4]
    yaw = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
    pitch = float(sys.argv[5]) if len(sys.argv) > 5 else 15.0
    width = int(sys.argv[6]) if len(sys.argv) > 6 else 1200
    photo = Image.open(env).convert('RGB')
    w, h = photo.size
    cx, cy = int((yaw / 360 + 0.5) * w), int((0.5 - pitch / 180) * h)
    cw, ch = int(w * 70 / 360), int(w * 70 / 360 * 2 / 3)          # about 70 degrees across
    box = (max(0, cx - cw // 2), max(0, cy - ch // 2), min(w, cx + cw // 2), min(h, cy + ch // 2))
    back = photo.crop(box).resize((width, width * 2 // 3), Image.LANCZOS).convert('RGBA')
    front = Image.open(render).convert('RGBA')
    scale = min(back.width * 0.8 / front.width, back.height * 0.8 / front.height)
    front = front.resize((int(front.width * scale), int(front.height * scale)), Image.LANCZOS)
    back.alpha_composite(front, ((back.width - front.width) // 2, (back.height - front.height) // 2))
    back.convert('RGB').save(out, quality=88)
    print('saved', out)


if __name__ == '__main__':
    main()
