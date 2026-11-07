from PIL import Image

# Let's inspect eye regions on each image
# In pixel coordinates for the original files:

# 1. KPOLI (1024x1024)
# Left eye (viewer's left): X~408, Y~370. Right eye: X~584, Y~370.

# 2. BALEN (1024x1024)
# Sunglasses centers: Left: X~405, Y~460. Right: X~588, Y~455.

# 3. HARKA (public/faces/harka.webp: 1024x1024)
# In original harka.webp:
# Left eye: X~420, Y~640. Right eye: X~580, Y~630.

# 4. DEUBA (1024x1024)
# Left eye: X~400, Y~425. Right eye: X~580, Y~445. (tilted)

# 5. PRACHANDA (1024x1024)
# Left eye: X~360, Y~420. Right eye: X~540, Y~410.

# 6. RABI (1024x1024)
# Left eye: X~430, Y~400. Right eye: X~610, Y~400.

# 7. GAGAN (1024x1024)
# Left eye: X~470, Y~385. Right eye: X~700, Y~390.

# 8. DURGA (durga_clean.png: 512x512)
# Left eye: X~205, Y~220. Right eye: X~320, Y~220.

# 9. GENZ MAYA (genz_maya.png: 307x266)
# Left eye: X~115, Y~100. Right eye: X~190, Y~100.

print('Manual landmark coordinates defined')
