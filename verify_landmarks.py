from PIL import Image, ImageDraw

EYE_LANDMARKS = {
    'kpoli': ('public/faces/kpoli.webp', (408, 368), (584, 368)),
    'balen': ('public/faces/balen.webp', (405, 460), (588, 455)),
    'harka': ('public/faces/harka.webp', (410, 640), (575, 630)),
    'deuba': ('public/faces/deuba.webp', (395, 425), (585, 445)),
    'prachanda': ('public/faces/prachanda.webp', (360, 420), (540, 410)),
    'rabi': ('public/faces/rabi.webp', (435, 400), (615, 400)),
    'gagan': ('public/faces/gagan.webp', (490, 385), (690, 390)),
    'durga': ('public/faces/durga_clean.png', (210, 220), (330, 220)),
    'genz': ('public/faces/genz_maya.png', (115, 100), (192, 100))
}

for name, (path, (lx, ly), (rx, ry)) in EYE_LANDMARKS.items():
    im = Image.open(path).convert('RGB')
    draw = ImageDraw.Draw(im)
    draw.ellipse([lx-10, ly-10, lx+10, ly+10], outline=(0, 255, 0), width=4)
    draw.ellipse([rx-10, ry-10, rx+10, ry+10], outline=(255, 0, 0), width=4)
    im.resize((300, 300)).save(f'check_eye_{name}.png')

print('All landmark checks saved!')
