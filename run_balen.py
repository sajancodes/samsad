import subprocess
from build_nepali_master import build_head_texture

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

# 1. Synthesize 360 Master Texture for Balen with mathematically perfect eye/sunglass alignment
gltf_tex = build_head_texture(
    char_id='balen',
    face_path='public/faces/balen.webp',
    topi_type='bhadgaunle',
    hair_type='black',
    skin_tone_mult=(0.95, 0.95, 0.95),
    face_scale_factor=1.15,
    face_shift_y=-124,
    face_radius_x=170.0,
    face_radius_y=190.0,
    topi_rim_front=270,
    topi_rim_back=360
)

# 2. Build 3D GLB in Blender with Jet-Black Suit Coat & Dark Trousers
print('Running Blender GLB builder for Balen...')
res = subprocess.run([
    BLENDER, '--background', '--python', 'build_nepali_blender_glb.py', '--',
    'balen', gltf_tex, '0.015', '0.015', '0.02', '0.015', '0.015', '0.02'
], capture_output=True, text=True)
print(res.stdout[-300:])

# 3. Render Multi-Angle Verification Images
for angle in ['front', 'side', 'back', 'three_quarter']:
    out_img = f'verify_balen_{angle}.png'
    subprocess.run([
        BLENDER, '--background', '--python', 'verify_render.py', '--',
        'public/models/balen.glb', out_img, angle
    ], capture_output=True, text=True)
    print(f'Rendered verify_balen_{angle}.png')

print('Balen 360 build & render complete!')
