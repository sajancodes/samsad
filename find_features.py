from PIL import Image, ImageDraw

def mark_and_save(name, path, eye_y, nose_y, mouth_y, center_x):
    im = Image.open(path).convert('RGB')
    w, h = im.size
    draw = ImageDraw.Draw(im)
    # Draw guides
    draw.line([(0, int(eye_y * h)), (w, int(eye_y * h))], fill=(0, 255, 0), width=3)
    draw.line([(0, int(nose_y * h)), (w, int(nose_y * h))], fill=(255, 255, 0), width=3)
    draw.line([(0, int(mouth_y * h)), (w, int(mouth_y * h))], fill=(255, 0, 0), width=3)
    draw.line([(int(center_x * w), 0), (int(center_x * w), h)], fill=(0, 255, 255), width=3)
    im.resize((300, 300)).save(f'guide_{name}.png')

# Let's test on each face
# Values are normalized fractions (0.0 to 1.0)
mark_and_save('kpoli', 'public/faces/kpoli.webp', 0.38, 0.46, 0.55, 0.48)
mark_and_save('balen', 'public/faces/balen.webp', 0.46, 0.54, 0.63, 0.50)
mark_and_save('harka', 'public/faces/harka_clean.png', 0.63, 0.77, 0.90, 0.50)
mark_and_save('deuba', 'public/faces/deuba.webp', 0.43, 0.54, 0.64, 0.52)
mark_and_save('prachanda', 'public/faces/prachanda.webp', 0.42, 0.49, 0.59, 0.47)
mark_and_save('rabi', 'public/faces/rabi.webp', 0.40, 0.49, 0.58, 0.50)
mark_and_save('gagan', 'public/faces/gagan.webp', 0.39, 0.49, 0.62, 0.54)
mark_and_save('durga', 'public/faces/durga_clean.png', 0.43, 0.55, 0.66, 0.48)
mark_and_save('genz', 'public/faces/genz_maya.png', 0.38, 0.52, 0.66, 0.50)
print('Guides saved')
