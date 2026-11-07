from PIL import Image

im = Image.open('public/faces/harka.webp')
w, h = im.size
# Harka is in the center-right of the image
# Let's crop X=200..1024, Y=0..850
crop = im.crop((int(w * 0.18), 0, int(w * 0.98), int(h * 0.85)))
crop = crop.resize((512, 512), Image.LANCZOS)
crop.save('public/faces/harka_clean.png')
print('Harka clean saved: public/faces/harka_clean.png')
