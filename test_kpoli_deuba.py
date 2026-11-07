import os
import math
import subprocess
import numpy as np
from PIL import Image, ImageFilter

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

def create_bhadgaunle_topi(width=1024, height=1024):
    arr = np.zeros((height, width, 3), dtype=np.float32)
    arr[:, :] = np.array([22.0, 22.0, 24.0])
    y = np.arange(height, dtype=np.float32)[:, None]
    x = np.arange(width, dtype=np.float32)[None, :]
    weave1 = np.sin((x + y) / 1024.0 * math.pi * 128.0) * 4.0
    weave2 = np.sin((x - y) / 1024.0 * math.pi * 128.0) * 4.0
    fold_light = np.cos(x / 1024.0 * 2.0 * math.pi) * 3.5
    np.random.seed(42)
    noise = np.random.normal(0, 1.5, (height, width, 3))
    arr = arr + weave1[:, :, None] + weave2[:, :, None] + fold_light[:, :, None] + noise
    return Image.fromarray(np.clip(arr, 14, 45).astype(np.uint8), 'RGB')

def create_dhaka_topi(width=1024, height=1024):
    im = Image.new('RGB', (width, height), (32, 16, 18))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(im)
    dw, dh = 32, 32
    for y in range(0, height, dh):
        for x in range(0, width, dw):
            idx = ((x // dw) + (y // dh)) % 4
            if idx == 0: col = (145, 30, 36)
            elif idx == 1: col = (25, 25, 28)
            elif idx == 2: col = (195, 148, 55)
            else: col = (38, 80, 48)
            cx, cy = x + dw//2, y + dh//2
            draw.polygon([(cx, y), (x + dw, cy), (cx, y + dh), (x, cy)], fill=col)
            draw.polygon([(cx, y + dh//4), (x + 3*dw//4, cy), (cx, y + 3*dh//4), (x + dw//4, cy)],
                         fill=(col[0]//2, col[1]//2, col[2]//2))
    return im.filter(ImageFilter.GaussianBlur(radius=0.6))

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

def build_pristine_head_canvas(skin_rgb, hair_color):
    w, h = 1024, 1024
    canvas = np.zeros((h, w, 3), dtype=np.float32)
    skin = np.array(skin_rgb, dtype=np.float32)
    canvas[:, :] = skin
    
    y_idx = np.arange(h, dtype=np.float32)[:, None]
    x_idx = np.arange(w, dtype=np.float32)[None, :]
    
    # Smooth anatomical neck gradient toward collar
    neck_grad = np.clip((y_idx - 520.0) / 300.0, 0.0, 1.0) * 0.16
    canvas = canvas * (1.0 - neck_grad[:, :, None])
    
    # Clean anatomical ears (strictly cartilage Y=340..460, excluding beard below 460)
    base = Image.open('base_head_upright.png').convert('RGB')
    base_arr = np.array(base, dtype=np.float32)
    dist_l = np.sqrt(((x_idx - 220.0) / 45.0)**2 + ((y_idx - 400.0) / 55.0)**2)
    dist_r = np.sqrt(((x_idx - 804.0) / 45.0)**2 + ((y_idx - 400.0) / 55.0)**2)
    ear_mask = np.clip(1.0 - np.minimum(dist_l, dist_r), 0.0, 1.0)**2
    # Clip off below Y=460 so no old beard reaches earlobe
    ear_mask = ear_mask * np.clip((465.0 - y_idx) / 10.0, 0.0, 1.0)
    
    ear_lum = (base_arr[:, :, 0]*0.299 + base_arr[:, :, 1]*0.587 + base_arr[:, :, 2]*0.114) / 185.0
    ear_shaded = skin * np.clip(ear_lum[:, :, None], 0.35, 1.05)
    canvas = canvas * (1.0 - ear_mask[:, :, None]) + ear_shaded * ear_mask[:, :, None]
    
    # Procedural high-fidelity hair (seamless horizontally)
    back_dist = np.minimum(x_idx, 1024.0 - x_idx)
    np.random.seed(101)
    hair_flow = np.sin(x_idx / 1024.0 * math.pi * 64.0) * 3.0 + np.sin(y_idx / 1024.0 * math.pi * 48.0) * 2.0
    hair_strands = np.random.normal(0, 4.0, (h, w))
    
    if hair_color == "black":
        hair_base = np.array([22.0, 21.0, 24.0], dtype=np.float32)
        hair_high = np.array([44.0, 42.0, 48.0], dtype=np.float32)
    elif hair_color == "grey":
        hair_base = np.array([125.0, 125.0, 130.0], dtype=np.float32)
        hair_high = np.array([195.0, 195.0, 205.0], dtype=np.float32)
    else: # salt_pepper
        hair_base = np.array([45.0, 45.0, 50.0], dtype=np.float32)
        hair_high = np.array([135.0, 135.0, 145.0], dtype=np.float32)
        
    hair_tex = hair_base + (hair_high - hair_base) * np.clip((hair_flow + hair_strands + 4.0) / 10.0, 0.0, 1.0)[:, :, None]
    
    # Hair covers upper cranium and sides/back down to nape (Y=610)
    nape_fade = np.clip((610.0 - y_idx) / 50.0, 0.0, 1.0)
    sides_back_weight = np.clip((320.0 - back_dist) / 45.0, 0.0, 1.0)
    crown_weight = np.clip((240.0 - y_idx) / 30.0, 0.0, 1.0)
    hair_mask = np.maximum(crown_weight, sides_back_weight) * nape_fade
    hair_mask = hair_mask * (1.0 - ear_mask * 0.95)
    
    canvas = canvas * (1.0 - hair_mask[:, :, None]) + hair_tex * hair_mask[:, :, None]
    return Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8), 'RGB')

def process_test_character(char_id, face_path, eyes, topi_type, hair_type, skin_rgb, bg_type):
    print(f"\nProcessing {char_id.upper()}...")
    w, h = 1024, 1024
    x_idx = np.arange(w, dtype=np.float32)[None, :]
    y_idx = np.arange(h, dtype=np.float32)[:, None]
    
    base = build_pristine_head_canvas(skin_rgb, hair_type)
    
    phi = (x_idx - 512.0) / 512.0 * math.pi
    if topi_type != 'none':
        rim_y = 350.0 - 115.0 * np.cos(phi) + 12.0 * np.cos(2.0 * phi)
        if topi_type == 'bhadgaunle':
            topi_canvas = create_bhadgaunle_topi(w, h)
        else:
            topi_canvas = create_dhaka_topi(w, h)
            
        topi_alpha = np.clip((rim_y - y_idx + 2.0) / 4.0, 0.0, 1.0)
        topi_mask = Image.fromarray((topi_alpha * 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(1.0))
        base.paste(topi_canvas, (0, 0), topi_mask)
        
        dist_to_rim = rim_y - y_idx
        rim_crease = np.exp(-((dist_to_rim) / 3.0)**2) * 0.45
        b_arr = np.array(base, dtype=np.float32)
        b_arr -= (rim_crease * 45.0)[:, :, None]
        base = Image.fromarray(np.clip(b_arr, 0, 255).astype(np.uint8), 'RGB')
    else:
        rim_y = np.full((1, w), 220.0, dtype=np.float32)
        
    src = Image.open(face_path).convert('RGBA')
    arr = np.array(src)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    if bg_type == 'white_flag':
        is_bg = (r > 175) & (g > 175) & (b > 175) & (np.abs(r.astype(int) - g.astype(int)) < 25)
        # also mask red flag
        is_flag = (r > 120) & (r > 1.25 * np.maximum(g, 1)) & (r > 1.25 * np.maximum(b, 1))
        is_bg = is_bg | is_flag
    elif bg_type == 'blue_studio':
        is_bg = (b > 100) & (b > 1.15 * r) & (b > 1.15 * g)
    else:
        is_bg = (r > 180) & (g > 180) & (b > 180)
    arr[is_bg, 3] = 0
    nobg_src = Image.fromarray(arr, 'RGBA')
    
    warped = align_face_affine(nobg_src, eyes[0], eyes[1])
    w_arr = np.array(warped, dtype=np.float32)
    
    # Extra cleanup for KP Oli flag / moon
    if char_id == 'kpoli':
        is_flag_or_moon = (x_idx > 660) & ((y_idx > 480) | (w_arr[:, :, 0] > 120))
        w_arr[is_flag_or_moon, 3] = 0.0
        
    alpha = w_arr[:, :, 3] / 255.0
    gate_x = np.clip((x_idx - 320.0) / 25.0, 0.0, 1.0) * np.clip((704.0 - x_idx) / 25.0, 0.0, 1.0)
    top_lim = (rim_y - 12.0) if topi_type != 'none' else 210.0
    gate_y = np.clip((y_idx - top_lim) / 18.0, 0.0, 1.0) * np.clip((675.0 - y_idx) / 35.0, 0.0, 1.0)
    face_alpha = alpha * gate_x * gate_y
    
    face_mask = Image.fromarray((face_alpha * 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(3.0))
    base.paste(Image.fromarray(w_arr[:, :, :3].astype(np.uint8)), (0, 0), face_mask)
    
    if topi_type != 'none':
        solid_alpha = np.clip((rim_y - 20.0 - y_idx) / 6.0, 0.0, 1.0)
        solid_mask = Image.fromarray((solid_alpha * 255).astype(np.uint8), 'L')
        base.paste(topi_canvas, (0, 0), solid_mask)
        
    tex_path = f'test_{char_id}_tex.png'
    gltf_img = base.transpose(Image.FLIP_TOP_BOTTOM)
    gltf_img.save(tex_path)
    
    # Build GLB
    cmd = [
        BLENDER, '--background', '--python', 'build_nepali_blender_glb.py', '--',
        f'{char_id}_test', tex_path,
        '0.2', '0.2', '0.2',
        '0.1', '0.1', '0.1'
    ]
    subprocess.run(cmd, check=True)
    
    for angle in ['front', 'side', 'back']:
        out_png = f'test_{char_id}_v14_{angle}.png'
        subprocess.run([
            BLENDER, '--background', '--python', 'verify_render.py', '--',
            f'public/models/{char_id}_test.glb', out_png, angle
        ], check=True)
        print(f"Rendered {out_png}")

if __name__ == '__main__':
    # Test KP Oli and Deuba
    process_test_character('kpoli', 'public/faces/kpoli.webp', ((408, 368), (584, 368)), 'bhadgaunle', 'salt_pepper', (218, 180, 156), 'white_flag')
    process_test_character('deuba', 'public/faces/deuba.webp', ((395, 425), (585, 445)), 'none', 'grey', (214, 175, 150), 'blue_studio')
