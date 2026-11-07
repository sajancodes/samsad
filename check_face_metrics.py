from PIL import Image

faces = {
    'kpoli': 'public/faces/kpoli.webp',
    'balen': 'public/faces/balen.webp',
    'harka': 'public/faces/harka_clean.png',
    'deuba': 'public/faces/deuba.webp',
    'prachanda': 'public/faces/prachanda.webp',
    'rabi': 'public/faces/rabi.webp',
    'gagan': 'public/faces/gagan.webp',
    'durga': 'public/faces/durga_clean.png',
    'genz': 'public/faces/genz_maya.png'
}

for name, path in faces.items():
    im = Image.open(path)
    w, h = im.size
    print(f'=== {name.upper()} ({path}) ===')
    print(f'Size: {w}x{h}')
