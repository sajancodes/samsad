from PIL import Image, ImageDraw

def find_coords(name, path):
    im = Image.open(path).convert('RGB')
    w, h = im.size
    print(f'{name}: {w}x{h}')

for name, path in [
    ('kpoli', 'public/faces/kpoli.webp'),
    ('balen', 'public/faces/balen.webp'),
    ('harka', 'public/faces/harka.webp'),
    ('deuba', 'public/faces/deuba.webp'),
    ('prachanda', 'public/faces/prachanda.webp'),
    ('rabi', 'public/faces/rabi.webp'),
    ('gagan', 'public/faces/gagan.webp'),
    ('durga', 'public/faces/durga_clean.png'),
    ('genz', 'public/faces/genz_maya.png')
]:
    find_coords(name, path)
