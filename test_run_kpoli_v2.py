import subprocess
import os
from build_master_v2 import build_character_texture_v2

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

# Generate V2 clean texture for KP Oli
tex_path = build_character_texture_v2(
    char_id='kpoli',
    face_path='public/faces/kpoli.webp',
    topi_type='bhadgaunle',
    hair_type='salt_pepper',
    skin_tone_rgb=(218, 180, 155),
    face_scale_factor=1.0,
    face_shift_y=-5,
    face_radius_x=170.0,
    face_radius_y=160.0,
    topi_rim_front=285,
    topi_rim_back=380
)

# Export to GLB via Blender
cmd = [
    BLENDER, '--background', '--python', 'build_nepali_blender_glb.py', '--',
    'kpoli', tex_path, '0.045', '0.05', '0.055', '0.03', '0.03', '0.035'
]
res = subprocess.run(cmd, capture_output=True, text=True)
print('Blender export:', res.stdout[-300:] if len(res.stdout) > 300 else res.stdout)
if res.stderr:
    print('Blender stderr:', res.stderr[-300:] if len(res.stderr) > 300 else res.stderr)

# Render front, side, and back views
for angle in ['front', 'side', 'back']:
    out_img = f'verify_kpoli_v2_{angle}.png'
    subprocess.run([
        BLENDER, '--background', '--python', 'verify_render.py', '--',
        'public/models/kpoli.glb', out_img, angle
    ], capture_output=True, text=True)
    print(f'Rendered {out_img}')
