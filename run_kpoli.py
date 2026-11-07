import subprocess
from build_nepali_master import build_head_texture

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

# 1. Synthesize 360 Master Texture with precise face radius
gltf_tex = build_head_texture(
    char_id='kpoli',
    face_path='public/faces/kpoli.webp',
    topi_type='bhadgaunle',
    hair_type='salt_pepper',
    skin_tone_mult=(1.02, 1.0, 0.98),
    face_scale_factor=1.0,
    face_shift_y=-5,
    face_radius_x=170.0,
    face_radius_y=160.0,
    topi_rim_front=285,
    topi_rim_back=365
)

# 2. Build 3D GLB in Blender with deep charcoal Nepali coat & dark trousers
print('Running Blender GLB builder...')
res = subprocess.run([
    BLENDER, '--background', '--python', 'build_nepali_blender_glb.py', '--',
    'kpoli', gltf_tex, '0.045', '0.05', '0.055', '0.03', '0.03', '0.035'
], capture_output=True, text=True)
print(res.stdout[-300:])

# 3. Render Multi-Angle Verification Images
for angle in ['front', 'side', 'back']:
    out_img = f'verify_kpoli_{angle}.png'
    subprocess.run([
        BLENDER, '--background', '--python', 'verify_render.py', '--',
        'public/models/kpoli.glb', out_img, angle
    ], capture_output=True, text=True)
    print(f'Rendered verify_kpoli_{angle}.png')

print('KP Oli 360 build & render complete!')
