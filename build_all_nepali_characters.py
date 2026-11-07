import subprocess
import os
import shutil
from build_nepali_master import build_head_texture

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

CHARACTERS = {
    'kpoli': {
        'face': 'public/faces/kpoli.webp',
        'topi': 'bhadgaunle',
        'hair': 'salt_pepper',
        'skin_mult': (1.02, 1.0, 0.98),
        'scale': 1.0,
        'shift_y': -5,
        'rad_x': 170.0,
        'rad_y': 160.0,
        'topi_rim_front': 285,
        'topi_rim_back': 365,
        'outfit_top': (0.045, 0.05, 0.055), # Charcoal Nepali coat
        'outfit_bot': (0.03, 0.03, 0.035),   # Dark trousers
    },
    'balen': {
        'face': 'public/faces/balen.webp',
        'topi': 'bhadgaunle',
        'hair': 'black',
        'skin_mult': (0.95, 0.95, 0.95),
        'scale': 1.15,
        'shift_y': -124,
        'rad_x': 170.0,
        'rad_y': 190.0,
        'topi_rim_front': 270,
        'topi_rim_back': 360,
        'outfit_top': (0.015, 0.015, 0.02), # Jet black suit coat
        'outfit_bot': (0.015, 0.015, 0.02), # Jet black trousers
    },
    'harka': {
        'face': 'public/faces/harka.webp',
        'topi': 'dhaka',
        'hair': 'black',
        'skin_mult': (0.98, 0.96, 0.94),
        'scale': 1.0,
        'shift_y': -10,
        'rad_x': 170.0,
        'rad_y': 165.0,
        'topi_rim_front': 285,
        'topi_rim_back': 365,
        'outfit_top': (0.05, 0.07, 0.035),  # Olive tactical Shramdan jacket
        'outfit_bot': (0.035, 0.035, 0.03), # Cargo pants
    },
    'deuba': {
        'face': 'public/faces/deuba.webp',
        'topi': 'bhadgaunle',
        'hair': 'grey',
        'skin_mult': (1.04, 1.0, 0.96),
        'scale': 1.0,
        'shift_y': -5,
        'rad_x': 170.0,
        'rad_y': 165.0,
        'topi_rim_front': 285,
        'topi_rim_back': 365,
        'outfit_top': (0.08, 0.085, 0.095), # Grey Nepali suit coat
        'outfit_bot': (0.03, 0.03, 0.035),  # Dark trousers
    },
    'prachanda': {
        'face': 'public/faces/prachanda.webp',
        'topi': 'bhadgaunle',
        'hair': 'grey',
        'skin_mult': (0.96, 0.94, 0.92),
        'scale': 1.0,
        'shift_y': -5,
        'rad_x': 170.0,
        'rad_y': 165.0,
        'topi_rim_front': 285,
        'topi_rim_back': 365,
        'outfit_top': (0.025, 0.025, 0.03), # Dark charcoal suit coat
        'outfit_bot': (0.02, 0.02, 0.025),  # Dark trousers
    },
    'rabi': {
        'face': 'public/faces/rabi.webp',
        'topi': 'none',
        'hair': 'black',
        'skin_mult': (0.98, 0.96, 0.95),
        'scale': 1.0,
        'shift_y': -10,
        'rad_x': 170.0,
        'rad_y': 175.0,
        'topi_rim_front': 250,
        'topi_rim_back': 340,
        'outfit_top': (0.015, 0.025, 0.06), # Deep navy slim-fit suit
        'outfit_bot': (0.015, 0.025, 0.06), # Navy trousers
    },
    'gagan': {
        'face': 'public/faces/gagan.webp',
        'topi': 'none',
        'hair': 'black',
        'skin_mult': (0.96, 0.94, 0.92),
        'scale': 1.0,
        'shift_y': -10,
        'rad_x': 170.0,
        'rad_y': 175.0,
        'topi_rim_front': 250,
        'topi_rim_back': 340,
        'outfit_top': (0.03, 0.04, 0.06),   # Indigo/charcoal formal jacket
        'outfit_bot': (0.025, 0.025, 0.03), # Dark trousers
    },
    'durga': {
        'face': 'public/faces/durga.webp',
        'topi': 'none',
        'hair': 'black',
        'skin_mult': (0.96, 0.94, 0.92),
        'scale': 1.0,
        'shift_y': -10,
        'rad_x': 170.0,
        'rad_y': 175.0,
        'topi_rim_front': 250,
        'topi_rim_back': 340,
        'outfit_top': (0.65, 0.65, 0.66),   # White Daura / Kurta
        'outfit_bot': (0.65, 0.65, 0.66),   # White trousers
    },
    'genz': {
        'face': 'public/faces/rabi.webp',
        'topi': 'none',
        'hair': 'black',
        'skin_mult': (0.95, 0.95, 0.95),
        'scale': 1.0,
        'shift_y': -10,
        'rad_x': 170.0,
        'rad_y': 175.0,
        'topi_rim_front': 250,
        'topi_rim_back': 340,
        'outfit_top': (0.02, 0.02, 0.025),  # Black streetwear jacket
        'outfit_bot': (0.015, 0.02, 0.035), # Dark denim
    }
}

def build_character(cid):
    cfg = CHARACTERS[cid]
    print(f'==============================================')
    print(f'BUILDING NEPALI CHARACTER: {cid.upper()}')
    print(f'==============================================')
    
    # 1. Synthesize 360 Texture
    tex_path = build_head_texture(
        char_id=cid,
        face_path=cfg['face'],
        topi_type=cfg['topi'],
        hair_type=cfg['hair'],
        skin_tone_mult=cfg['skin_mult'],
        face_scale_factor=cfg['scale'],
        face_shift_y=cfg['shift_y'],
        face_radius_x=cfg['rad_x'],
        face_radius_y=cfg['rad_y'],
        topi_rim_front=cfg['topi_rim_front'],
        topi_rim_back=cfg['topi_rim_back']
    )
    
    # 2. Build GLB via Blender
    top_col = [str(c) for c in cfg['outfit_top']]
    bot_col = [str(c) for c in cfg['outfit_bot']]
    
    cmd = [
        BLENDER, '--background', '--python', 'build_nepali_blender_glb.py', '--',
        cid, tex_path, top_col[0], top_col[1], top_col[2], bot_col[0], bot_col[1], bot_col[2]
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f'Error building {cid}: {res.stderr}')
    else:
        print(f'Blender export successful for {cid}!')
        
    # 3. Render Multi-Angle Verification Views
    for angle in ['front', 'side', 'back']:
        out_img = f'verify_{cid}_{angle}.png'
        subprocess.run([
            BLENDER, '--background', '--python', 'verify_render.py', '--',
            f'public/models/{cid}.glb', out_img, angle
        ], capture_output=True, text=True)
        print(f'  Rendered {out_img}')

if __name__ == '__main__':
    import sys
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(CHARACTERS.keys())
    for t in targets:
        if t in CHARACTERS:
            build_character(t)
    print('ALL REQUESTED NEPALI CHARACTERS BUILT SUCCESSFULLY!')
