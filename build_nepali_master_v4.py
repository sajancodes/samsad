import os
import math
import subprocess
import shutil
from collections import deque
import numpy as np
from PIL import Image, ImageFilter

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

# ==============================================================================
# PROCEDURAL FABRIC GENERATORS
# ==============================================================================
def create_bhadgaunle_topi(width=1024, height=1024):
    """Generates horizontally seamless authentic black Bhadgaunle diamond twill fabric."""
    arr = np.zeros((height, width, 3), dtype=np.float32)
    arr[:, :] = np.array([20.0, 20.0, 22.0])
    
    y = np.arange(height, dtype=np.float32)[:, None]
    x = np.arange(width, dtype=np.float32)[None, :]
    
    # 45-degree cross twill weave (loops horizontally across 1024 pixels)
    weave1 = np.sin((x + y) / 1024.0 * math.pi * 128.0) * 3.5
    weave2 = np.sin((x - y) / 1024.0 * math.pi * 128.0) * 3.5
    
    # Horizontal fold lighting sheen
    fold_light = np.cos(x / 1024.0 * 2.0 * math.pi) * 3.0
    
    np.random.seed(42)
    noise = np.random.normal(0, 1.2, (height, width, 3))
    
    arr = arr + weave1[:, :, None] + weave2[:, :, None] + fold_light[:, :, None] + noise
    return Image.fromarray(np.clip(arr, 12, 40).astype(np.uint8), 'RGB')

def create_dhaka_topi(width=1024, height=1024):
    """Generates horizontally seamless authentic Nepali Dhaka geometric pattern."""
    im = Image.new('RGB', (width, height), (32, 16, 18))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(im)
    
    dw, dh = 32, 32
    for y in range(0, height, dh):
        for x in range(0, width, dw):
            idx = ((x // dw) + (y // dh)) % 4
            if idx == 0:
                col = (145, 30, 36) # Crimson
            elif idx == 1:
                col = (25, 25, 28)  # Charcoal
            elif idx == 2:
                col = (195, 148, 55) # Ochre Gold
            else:
                col = (38, 80, 48)   # Forest Green
            
            cx, cy = x + dw//2, y + dh//2
            draw.polygon([(cx, y), (x + dw, cy), (cx, y + dh), (x, cy)], fill=col)
            draw.polygon([(cx, y + dh//4), (x + 3*dw//4, cy), (cx, y + 3*dh//4), (x + dw//4, cy)],
                         fill=(col[0]//2, col[1]//2, col[2]//2))
            
    return im.filter(ImageFilter.GaussianBlur(radius=0.6))

# ==============================================================================
# 2D AFFINE & CYLINDRICAL TRANSFORM TOOLS
# ==============================================================================
def align_face_affine(src_img, src_left_eye, src_right_eye, dst_left_eye=(421, 330), dst_right_eye=(607, 336), out_size=(1024, 1024)):
    v_src = (src_right_eye[0] - src_left_eye[0], src_right_eye[1] - src_left_eye[1])
    v_dst = (dst_right_eye[0] - dst_left_eye[0], dst_right_eye[1] - dst_left_eye[1])
    scale = math.hypot(v_dst[0], v_dst[1]) / math.hypot(v_src[0], v_src[1])
    angle = math.atan2(v_dst[1], v_dst[0]) - math.atan2(v_src[1], v_src[0])
    
    mid_src = ((src_left_eye[0] + src_right_eye[0]) / 2.0, (src_left_eye[1] + src_right_eye[1]) / 2.0)
    mid_dst = ((dst_left_eye[0] + dst_right_eye[0]) / 2.0, (dst_left_eye[1] + dst_right_eye[1]) / 2.0)
    
    inv_s = 1.0 / scale
    c = math.cos(-angle) * inv_s
    s = math.sin(-angle) * inv_s
    tx = mid_src[0] - c * mid_dst[0] + s * mid_dst[1]
    ty = mid_src[1] - s * mid_dst[0] - c * mid_dst[1]
    return src_img.transform(out_size, Image.AFFINE, (c, -s, tx, s, c, ty), resample=Image.BICUBIC)

def cylindrical_unwrap_face(src_rgba, fcx=514.0, R_uv=320.0, curve=2.3):
    arr = np.array(src_rgba, dtype=np.float32)
    h, w, c = arr.shape
    out = np.zeros_like(arr)
    for x_out in range(w):
        dx_uv = (x_out - fcx) / R_uv
        if abs(dx_uv) < 1.0:
            theta = dx_uv * (math.pi / curve)
            dx_photo = math.sin(theta)
            x_src = fcx + dx_photo * R_uv
            x0 = int(math.floor(x_src))
            x1 = min(w - 1, x0 + 1)
            fx = x_src - x0
            if 0 <= x0 < w:
                out[:, x_out] = arr[:, x0] * (1.0 - fx) + arr[:, x1] * fx
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), mode=src_rgba.mode)

# ==============================================================================
# BACKGROUND REMOVAL PER CHARACTER TYPE
# ==============================================================================
def remove_background(im, bg_type):
    rgba = im.convert('RGBA')
    arr = np.array(rgba)
    h, w, _ = arr.shape
    visited = np.zeros((h, w), dtype=bool)
    bg_mask = np.zeros((h, w), dtype=bool)
    q = deque()
    
    # Perimeter seeds
    for y in range(h):
        q.append((y, 0)); q.append((y, w - 1))
        visited[y, 0] = True; visited[y, w - 1] = True
    for x in range(w):
        q.append((0, x)); visited[0, x] = True
        
    while q:
        y, x = q.popleft()
        r, g, b = int(arr[y, x, 0]), int(arr[y, x, 1]), int(arr[y, x, 2])
        is_bg = False
        
        if bg_type == 'white_flag':
            # KP Oli: white wall or red flag or white moon
            is_wall = (r > 175 and g > 175 and b > 175 and abs(r - g) < 25 and abs(r - b) < 25)
            is_flag = (r > 120 and r > 1.30 * max(1, g) and r > 1.30 * max(1, b))
            is_moon = (x > 640 and r > 170 and g > 170 and b > 170)
            is_bg = is_wall or is_flag or is_moon
        elif bg_type == 'grey_studio':
            # Balen: light grey studio
            is_bg = (r > 185 and g > 185 and b > 185 and abs(r - g) < 20 and abs(r - b) < 20)
        elif bg_type == 'green_nature':
            # Harka: foliage / background rocks
            is_green = (g > 70 and g > 1.15 * r and g > 1.15 * b)
            is_rock = (r > 100 and g > 100 and b > 100 and abs(r - g) < 20 and abs(r - b) < 20 and (x < 150 or x > 380))
            is_bg = is_green or is_rock
        elif bg_type == 'blue_studio':
            # Deuba: solid blue studio
            is_bg = (b > 100 and b > 1.15 * r and b > 1.15 * g)
        elif bg_type in ('white_indoor', 'white_wall', 'white_banner'):
            # Light wall / conference banner
            is_bg = (r > 170 and g > 170 and b > 170 and abs(r - g) < 25 and abs(r - b) < 25) or (b > 120 and b > 1.25 * r)
        elif bg_type == 'cyber_glow':
            # Outer dark space
            is_bg = (r < 30 and g < 30 and b < 30)
            
        if is_bg:
            bg_mask[y, x] = True
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                    visited[ny, nx] = True
                    q.append((ny, nx))
                    
    arr[bg_mask, 3] = 0
    return Image.fromarray(arr, 'RGBA')

# ==============================================================================
# CHARACTER ROSTER CONFIGURATION
# ==============================================================================
CHARACTERS = {
    'kpoli': {
        'face': 'public/faces/kpoli.webp',
        'eyes': ((408, 368), (584, 368)),
        'topi': 'bhadgaunle',
        'hair': 'salt_pepper',
        'skin_rgb': (218, 180, 156),
        'bg_type': 'white_flag',
        'rim_front': 235,
        'rim_back': 410,
        'chin_y': 620,
        'neck_fade_y': 660,
        'outfit_top': (0.42, 0.43, 0.45, 1.0),
        'outfit_bot': (0.22, 0.23, 0.25, 1.0),
        'legacy': 'modi',
    },
    'balen': {
        'face': 'public/faces/balen.webp',
        'eyes': ((405, 460), (588, 455)),
        'topi': 'bhadgaunle',
        'hair': 'black',
        'skin_rgb': (208, 168, 142),
        'bg_type': 'grey_studio',
        'rim_front': 230,
        'rim_back': 410,
        'chin_y': 650,
        'neck_fade_y': 680,
        'outfit_top': (0.015, 0.015, 0.02, 1.0),
        'outfit_bot': (0.015, 0.015, 0.02, 1.0),
        'legacy': 'yogi',
    },
    'harka': {
        'face': 'public/faces/harka_clean.png',
        'eyes': ((165, 320), (305, 315)),
        'topi': 'dhaka',
        'hair': 'black',
        'skin_rgb': (210, 170, 145),
        'bg_type': 'green_nature',
        'rim_front': 235,
        'rim_back': 410,
        'chin_y': 620,
        'neck_fade_y': 660,
        'outfit_top': (0.05, 0.07, 0.035, 1.0),
        'outfit_bot': (0.035, 0.035, 0.03, 1.0),
        'legacy': 'didi',
    },
    'deuba': {
        'face': 'public/faces/deuba.webp',
        'eyes': ((395, 425), (585, 445)),
        'topi': 'none',
        'hair': 'grey',
        'skin_rgb': (214, 175, 150),
        'bg_type': 'blue_studio',
        'rim_front': 210,
        'rim_back': 580,
        'chin_y': 630,
        'neck_fade_y': 670,
        'outfit_top': (0.08, 0.085, 0.095, 1.0),
        'outfit_bot': (0.03, 0.03, 0.035, 1.0),
        'legacy': 'nitin',
    },
    'prachanda': {
        'face': 'public/faces/prachanda.webp',
        'eyes': ((360, 420), (540, 410)),
        'topi': 'bhadgaunle',
        'hair': 'grey',
        'skin_rgb': (212, 172, 148),
        'bg_type': 'white_indoor',
        'rim_front': 235,
        'rim_back': 410,
        'chin_y': 620,
        'neck_fade_y': 660,
        'outfit_top': (0.04, 0.045, 0.05, 1.0),
        'outfit_bot': (0.025, 0.025, 0.03, 1.0),
        'legacy': 'lalu',
    },
    'rabi': {
        'face': 'public/faces/rabi.webp',
        'eyes': ((435, 400), (615, 400)),
        'topi': 'none',
        'hair': 'black',
        'skin_rgb': (216, 176, 152),
        'bg_type': 'white_wall',
        'rim_front': 210,
        'rim_back': 580,
        'chin_y': 640,
        'neck_fade_y': 675,
        'outfit_top': (0.015, 0.025, 0.06, 1.0),
        'outfit_bot': (0.015, 0.025, 0.06, 1.0),
        'legacy': 'ravi',
    },
    'gagan': {
        'face': 'public/faces/gagan.webp',
        'eyes': ((533, 395), (742, 395)),
        'topi': 'none',
        'hair': 'black',
        'skin_rgb': (210, 168, 144),
        'bg_type': 'white_indoor',
        'rim_front': 210,
        'rim_back': 580,
        'chin_y': 630,
        'neck_fade_y': 665,
        'outfit_top': (0.03, 0.04, 0.065, 1.0),
        'outfit_bot': (0.025, 0.025, 0.03, 1.0),
        'legacy': 'rahul',
    },
    'durga': {
        'face': 'public/faces/durga_hq.png',
        'eyes': ((880, 375), (1070, 420)),
        'topi': 'none',
        'hair': 'black',
        'skin_rgb': (214, 172, 148),
        'bg_type': 'white_banner',
        'rim_front': 210,
        'rim_back': 580,
        'chin_y': 630,
        'neck_fade_y': 670,
        'outfit_top': (0.75, 0.75, 0.77, 1.0),
        'outfit_bot': (0.75, 0.75, 0.77, 1.0),
        'legacy': 'trump',
    },
    'genz': {
        'face': 'public/faces/genz_maya.png',
        'eyes': ((115, 100), (192, 100)),
        'topi': 'none',
        'hair': 'black',
        'skin_rgb': (218, 176, 154),
        'bg_type': 'cyber_glow',
        'rim_front': 210,
        'rim_back': 580,
        'chin_y': 620,
        'neck_fade_y': 660,
        'outfit_top': (0.02, 0.02, 0.025, 1.0),
        'outfit_bot': (0.015, 0.02, 0.035, 1.0),
        'legacy': 'mbapu',
    },
}

# ==============================================================================
# MASTER 360 TEXTURE SYNTHESIZER
# ==============================================================================
def synthesize_character_texture(char_id):
    cfg = CHARACTERS[char_id]
    print(f'Synthesizing 360 master texture for: {char_id.upper()}')
    w, h = 1024, 1024
    
    # 1. Base head with natural neck, ears, occipital
    base = Image.open('base_head_upright.png').convert('RGB')
    base_arr = np.array(base, dtype=np.float32)
    
    # Color-grade hair on sides and back
    lum = base_arr[:, :, 0]*0.299 + base_arr[:, :, 1]*0.587 + base_arr[:, :, 2]*0.114
    hair_type = cfg['hair']
    target_hair = np.zeros_like(base_arr)
    if hair_type == 'grey':
        target_hair[:, :, 0] = lum * 0.95 + 45.0
        target_hair[:, :, 1] = lum * 0.95 + 45.0
        target_hair[:, :, 2] = lum * 1.00 + 48.0
    elif hair_type == 'salt_pepper':
        target_hair[:, :, 0] = lum * 0.70 + 22.0
        target_hair[:, :, 1] = lum * 0.70 + 22.0
        target_hair[:, :, 2] = lum * 0.74 + 25.0
    else: # black
        target_hair = base_arr * 0.22 + 6.0
        
    x_idx = np.arange(w, dtype=np.float32)[None, :]
    y_idx = np.arange(h, dtype=np.float32)[:, None]
    back_dist = np.minimum(x_idx, 1024.0 - x_idx)
    
    if cfg['topi'] != 'none':
        # Hair active below Topi rim on sides and back
        hair_weight = np.clip((280.0 - back_dist) / 30.0, 0.0, 1.0) * np.clip((610.0 - y_idx) / 50.0, 0.0, 1.0)
    else:
        # Full hair covering upper crown and sides/back
        crown_hair = np.clip((cfg['rim_front'] + 20.0 - y_idx) / 30.0, 0.0, 1.0)
        back_hair = np.clip((280.0 - back_dist) / 30.0, 0.0, 1.0) * np.clip((610.0 - y_idx) / 50.0, 0.0, 1.0)
        hair_weight = np.maximum(crown_hair, back_hair)
        
    base_arr = base_arr * (1.0 - hair_weight[:, :, None]) + target_hair * hair_weight[:, :, None]
    
    # Clean skin on chin & entire front neck (eliminates all old beard / zombie patches)
    skin_tone = np.array(cfg['skin_rgb'], dtype=np.float32)
    clean_neck = np.clip((back_dist - 230.0) / 40.0, 0.0, 1.0) * np.clip((y_idx - 460.0) / 40.0, 0.0, 1.0)
    base_arr = base_arr * (1.0 - clean_neck[:, :, None]) + skin_tone * clean_neck[:, :, None]
    
    base = Image.fromarray(np.clip(base_arr, 0, 255).astype(np.uint8), 'RGB')
    
    # 2. Add Topi (if wearing Topi)
    if cfg['topi'] != 'none':
        rf = cfg['rim_front']
        rb = cfg['rim_back']
        rim_mid = (rf + rb) / 2.0
        rim_amp = (rb - rf) / 2.0
        rim_y = rim_mid - rim_amp * np.cos((x_idx - 512.0) / 512.0 * math.pi)
        
        if cfg['topi'] == 'bhadgaunle':
            topi_canvas = create_bhadgaunle_topi(w, h)
        else: # dhaka
            topi_canvas = create_dhaka_topi(w, h)
            
        topi_alpha = np.clip((rim_y - y_idx + 2.0) / 5.0, 0.0, 1.0)
        topi_mask = Image.fromarray((topi_alpha * 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(1.2))
        base.paste(topi_canvas, (0, 0), topi_mask)
        
        # 3D folded edge crease shadow
        dist_to_rim = rim_y - y_idx
        rim_crease = np.exp(-((dist_to_rim) / 2.5)**2) * 0.45
        b_arr = np.array(base, dtype=np.float32)
        b_arr -= (rim_crease * 45.0)[:, :, None]
        base = Image.fromarray(np.clip(b_arr, 0, 255).astype(np.uint8), 'RGB')
    else:
        rim_y = np.full((1, w), cfg['rim_front'], dtype=np.float32)
        
    # 3. Clean background & Warp front photo portrait
    src = Image.open(cfg['face'])
    nobg_src = remove_background(src, cfg['bg_type'])
    warped_nobg = align_face_affine(nobg_src, cfg['eyes'][0], cfg['eyes'][1])
    cyl_face = cylindrical_unwrap_face(warped_nobg)
    
    # Remove any border flag/moon artifacts if char is KP Oli
    w_arr = np.array(cyl_face, dtype=np.float32)
    if char_id == 'kpoli':
        r, g, b = w_arr[:, :, 0], w_arr[:, :, 1], w_arr[:, :, 2]
        is_flag = (r > 120) & (r > 1.25 * np.maximum(g, 1))
        is_moon = (r > 165) & (g > 165) & (b > 165)
        is_flag_or_moon = (x_idx > 660) & ((y_idx > 480) | is_flag | is_moon)
        w_arr[is_flag_or_moon, 3] = 0.0
        
    alpha = w_arr[:, :, 3] / 255.0
    
    # 4. Composite Face
    gate_x = np.clip((x_idx - 250.0) / 25.0, 0.0, 1.0) * np.clip((774.0 - x_idx) / 25.0, 0.0, 1.0)
    top_limit = rim_y - 15.0 if cfg['topi'] != 'none' else (cfg['rim_front'] - 10.0)
    gate_y = np.clip((y_idx - top_limit) / 20.0, 0.0, 1.0) * np.clip((cfg['neck_fade_y'] - y_idx) / (cfg['neck_fade_y'] - cfg['chin_y']), 0.0, 1.0)
    face_alpha = alpha * gate_x * gate_y
    
    face_mask = Image.fromarray((face_alpha * 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(3.5))
    base.paste(Image.fromarray(w_arr[:, :, :3].astype(np.uint8)), (0, 0), face_mask)
    
    # 5. Topi crown safety: Y < rim_y - 20 is 100% solid Topi
    if cfg['topi'] != 'none':
        solid_alpha = np.clip((rim_y - 20.0 - y_idx) / 8.0, 0.0, 1.0)
        solid_mask = Image.fromarray((solid_alpha * 255).astype(np.uint8), 'L')
        base.paste(topi_canvas, (0, 0), solid_mask)
        
    # Save preview and glTF texture
    prev_path = f'preview_{char_id}_v4.png'
    base.save(prev_path)
    
    tex_path = f'{char_id}_head_tex.png'
    gltf_img = base.transpose(Image.FLIP_TOP_BOTTOM)
    gltf_img.save(tex_path)
    print(f'  Saved texture: {tex_path} and preview: {prev_path}')
    return tex_path

# ==============================================================================
# BLENDER GLB BUILD & MULTI-ANGLE VERIFICATION RENDER
# ==============================================================================
def build_and_render_character(char_id):
    cfg = CHARACTERS[char_id]
    print(f'\n======================================================')
    print(f'BUILDING 3D GLB & RENDERING: {char_id.upper()}')
    print(f'======================================================')
    
    tex_path = synthesize_character_texture(char_id)
    
    top_col = [str(c) for c in cfg['outfit_top']]
    bot_col = [str(c) for c in cfg['outfit_bot']]
    
    cmd = [
        BLENDER, '--background', '--python', 'build_nepali_blender_glb.py', '--',
        char_id, tex_path,
        top_col[0], top_col[1], top_col[2],
        bot_col[0], bot_col[1], bot_col[2]
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f'Error building {char_id}: {res.stderr}')
    else:
        print(f'GLB export complete for {char_id}!')
        
    for angle in ['front', 'side', 'back']:
        out_img = f'verify_{char_id}_{angle}.png'
        subprocess.run([
            BLENDER, '--background', '--python', 'verify_render.py', '--',
            f'public/models/{char_id}.glb', out_img, angle
        ], capture_output=True, text=True)
        print(f'  Rendered {out_img}')

if __name__ == '__main__':
    import sys
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(CHARACTERS.keys())
    for t in targets:
        if t in CHARACTERS:
            build_and_render_character(t)
    print('\nALL TARGETS COMPLETED SUCCESSFULLY!')
