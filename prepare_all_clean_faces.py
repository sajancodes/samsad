from PIL import Image

# 1. KPOLI
im_kpoli = Image.open('public/faces/kpoli.webp').convert('RGB')
# Already centered, resize to 512x512
im_kpoli.resize((512, 512), Image.LANCZOS).save('public/faces/aligned_kpoli.png')

# 2. BALEN
im_balen = Image.open('public/faces/balen.webp').convert('RGB')
# Balen is tall with Topi. Eyes at Y=470.
# Crop Y=100..900 so face is centered
im_balen_cropped = im_balen.crop((60, 150, 964, 950)).resize((512, 512), Image.LANCZOS)
im_balen_cropped.save('public/faces/aligned_balen.png')

# 3. HARKA
im_harka = Image.open('public/faces/harka_clean.png').convert('RGB')
# Harka eyes are at Y=320, mouth at Y=460.
# Crop to center face: Y=140..512, X=50..470
w, h = im_harka.size
im_harka_crop = im_harka.crop((40, 130, 480, 510)).resize((512, 512), Image.LANCZOS)
im_harka_crop.save('public/faces/aligned_harka.png')

# 4. DEUBA
im_deuba = Image.open('public/faces/deuba.webp').convert('RGB')
# Rotate -4.5 degrees to level eyes
im_deuba_rot = im_deuba.rotate(-4.5, resample=Image.BICUBIC)
im_deuba_crop = im_deuba_rot.crop((60, 100, 964, 950)).resize((512, 512), Image.LANCZOS)
im_deuba_crop.save('public/faces/aligned_deuba.png')

# 5. PRACHANDA
im_prachanda = Image.open('public/faces/prachanda.webp').convert('RGB')
# Rotate -3.0 degrees to level glasses
im_prachanda_rot = im_prachanda.rotate(-3.0, resample=Image.BICUBIC)
im_prachanda_crop = im_prachanda_rot.crop((50, 120, 950, 950)).resize((512, 512), Image.LANCZOS)
im_prachanda_crop.save('public/faces/aligned_prachanda.png')

# 6. RABI
im_rabi = Image.open('public/faces/rabi.webp').convert('RGB')
im_rabi_crop = im_rabi.crop((50, 80, 950, 950)).resize((512, 512), Image.LANCZOS)
im_rabi_crop.save('public/faces/aligned_rabi.png')

# 7. GAGAN
im_gagan = Image.open('public/faces/gagan.webp').convert('RGB')
im_gagan_crop = im_gagan.crop((50, 80, 950, 950)).resize((512, 512), Image.LANCZOS)
im_gagan_crop.save('public/faces/aligned_gagan.png')

# 8. DURGA
im_durga = Image.open('public/faces/durga_clean.png').convert('RGB')
im_durga.resize((512, 512), Image.LANCZOS).save('public/faces/aligned_durga.png')

# 9. GENZ MAYA
im_genz = Image.open('public/faces/genz_maya.png').convert('RGB')
im_genz.resize((512, 512), Image.LANCZOS).save('public/faces/aligned_genz.png')

print('ALL 9 CLEAN ALIGNED FACES CREATED SUCCESSFULLY!')
