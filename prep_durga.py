from PIL import Image

im = Image.open('public/faces/durga.webp')
w, h = im.size
# Crop Durga Prasai: centered on his face
durga_crop = im.crop((int(w * 0.44), int(h * 0.05), int(w * 0.98), int(h * 0.65)))
durga_crop = durga_crop.resize((512, 512), Image.LANCZOS)
durga_crop.save('public/faces/durga_clean.png')
print('Durga clean saved: public/faces/durga_clean.png')
