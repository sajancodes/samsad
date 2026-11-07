import os
import math
import subprocess
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

def create_bhadgaunle_topi(width=1024, height=1024):
    """Generates horizontally seamless authentic black Bhadgaunle diamond twill fabric."""
    arr = np.zeros((height, width, 3), dtype=np.float32)
    arr[:, :] = np.array([22.0, 22.0, 24.0])
    
    y = np.arange(height, dtype=np.float32)[:, None]
    x = np.arange(width, dtype=np.float32)[None, :]
    
    # 45-degree cross twill weave (loops horizontally across 1024 pixels)
    weave1 = np.sin((x + y) / 1024.0 * math.pi * 128.0) * 4.0
    weave2 = np.sin((x - y) / 1024.0 * math.pi * 128.0) * 4.0
    
    # Horizontal fold lighting sheen
    fold_light = np.cos(x / 1024.0 * 2.0 * math.pi) * 3.5
    
    np.random.seed(42)
    noise = np.random.normal(0, 1.5, (height, width, 3))
    
    arr = arr + weave1[:, :, None] + weave2[:, :, None] + fold_light[:, :, None] + noise
    return Image.fromarray(np.clip(arr, 14, 45).astype(np.uint8), 'RGB')

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

def build_pristine_head_canvas(skin_rgb=(208, 168, 142), hair_color="black"):
    w, h = 1024, 1024
    canvas = np.zeros((h, w, 3), dtype=np.float32)
    
    # 1. Base skin tone across entire canvas
    skin = np.array(skin_rgb, dtype=np.float32)
    canvas[:, :] = skin
    
    # Anatomical neck ambient shading (subtle darkening toward collar Y=820 and under jaw)
    y_idx = np.arange(h, dtype=np.float32)[:, None]
    x_idx = np.arange(w, dtype=np.float32)[None, :]
    neck_grad = np.clip((y_idx - 520.0) / 300.0, 0.0, 1.0) * 0.16
    canvas = canvas * (1.0 - neck_grad[:, :, None])
    
    # 2. Extract clean ears from base_head_upright.png
    base = Image.open('base_head_upright.png').convert('RGB')
    base_arr = np.array(base, dtype=np.float32)
    
    # Ear regions: Left (X=170..270, Y=330..490), Right (X=750..850, Y=330..490)
    dist_l = np.sqrt(((x_idx - 220.0) / 50.0)**2 + ((y_idx - 410.0) / 80.0)**2)
    dist_r = np.sqrt(((x_idx - 804.0) / 50.0)**2 + ((y_idx - 410.0) / 80.0)**2)
    ear_mask = np.clip(1.0 - np.minimum(dist_l, dist_r), 0.0, 1.0)
    ear_mask = ear_mask**2
    
    # Retint ear to match skin tone while preserving cartilage folds & shadows
    ear_lum = (base_arr[:, :, 0]*0.299 + base_arr[:, :, 1]*0.587 + base_arr[:, :, 2]*0.114) / 185.0
    ear_shaded = skin * np.clip(ear_lum[:, :, None], 0.35, 1.05)
    canvas = canvas * (1.0 - ear_mask[:, :, None]) + ear_shaded * ear_mask[:, :, None]
    
    # 3. Procedural high-fidelity combed hair on cranium, sides, and nape
    back_dist = np.minimum(x_idx, 1024.0 - x_idx) # Distance to back midline (X=0/1024)
    
    # Natural hair texture synthesis (seamless horizontally)
    np.random.seed(101)
    hair_flow = np.sin(x_idx / 1024.0 * math.pi * 64.0) * 3.0 + np.sin(y_idx / 1024.0 * math.pi * 48.0) * 2.0
    hair_strands = np.random.normal(0, 4.0, (h, w))
    
    if hair_color == "black":
        hair_base = np.array([22.0, 21.0, 24.0], dtype=np.float32)
        hair_high = np.array([44.0, 42.0, 48.0], dtype=np.float32)
    elif hair_color == "grey":
        hair_base = np.array([120.0, 120.0, 126.0], dtype=np.float32)
        hair_high = np.array([195.0, 195.0, 205.0], dtype=np.float32)
    else: # salt_pepper
        hair_base = np.array([45.0, 45.0, 50.0], dtype=np.float32)
        hair_high = np.array([135.0, 135.0, 145.0], dtype=np.float32)
        
    hair_tex = hair_base + (hair_high - hair_base) * np.clip((hair_flow + hair_strands + 4.0) / 10.0, 0.0, 1.0)[:, :, None]
    
    # Hair coverage mask: covers upper cranium and sides/back down to nape (Y=590)
    nape_fade = np.clip((610.0 - y_idx) / 50.0, 0.0, 1.0)
    sides_back_weight = np.clip((320.0 - back_dist) / 45.0, 0.0, 1.0)
    crown_weight = np.clip((240.0 - y_idx) / 30.0, 0.0, 1.0)
    hair_mask = np.maximum(crown_weight, sides_back_weight) * nape_fade
    
    # Exclude ear area from hair mask so ears stay clean
    hair_mask = hair_mask * (1.0 - ear_mask * 0.95)
    
    canvas = canvas * (1.0 - hair_mask[:, :, None]) + hair_tex * hair_mask[:, :, None]
    
    return Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8), 'RGB')

def build_test_balen():
    print("Building Balen v14 with Perfect Ear & Neck Blending...")
    w, h = 1024, 1024
    x_idx = np.arange(w, dtype=np.float32)[None, :]
    y_idx = np.arange(h, dtype=np.float32)[:, None]
    
    # 1. Clean anatomical base canvas
    base = build_pristine_head_canvas(skin_rgb=(208, 168, 142), hair_color="black")
    
    # 2. Authentic Bhadgaunle Topi covering cranium down to occiput
    # Front (X=512): Y=235 (forehead)
    # Sides (X=220 / 804): Y=335 (just above ears)
    # Back (X=0 / 1024): Y=470 (lower occiput)
    phi = (x_idx - 512.0) / 512.0 * math.pi
    rim_y = 350.0 - 115.0 * np.cos(phi) + 12.0 * np.cos(2.0 * phi)
    
    topi_canvas = create_bhadgaunle_topi(w, h)
    
    # Topi mask: 1.0 above rim_y, soft edge
    topi_alpha = np.clip((rim_y - y_idx + 2.0) / 4.0, 0.0, 1.0)
    topi_mask = Image.fromarray((topi_alpha * 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(1.0))
    base.paste(topi_canvas, (0, 0), topi_mask)
    
    # Physical rim crease shadow
    dist_to_rim = rim_y - y_idx
    rim_crease = np.exp(-((dist_to_rim) / 3.0)**2) * 0.45
    b_arr = np.array(base, dtype=np.float32)
    b_arr -= (rim_crease * 45.0)[:, :, None]
    base = Image.fromarray(np.clip(b_arr, 0, 255).astype(np.uint8), 'RGB')
    
    # 3. Balen photo portrait background removal & warp
    src = Image.open('public/faces/balen.webp').convert('RGBA')
    arr = np.array(src)
    # Studio grey background removal
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    is_bg = (r > 175) & (g > 175) & (b > 175) & (np.abs(r.astype(int) - g.astype(int)) < 22) & (np.abs(r.astype(int) - b.astype(int)) < 22)
    arr[is_bg, 3] = 0
    nobg_src = Image.fromarray(arr, 'RGBA')
    
    # Align affine to standard eye sockets: (421, 330) and (607, 336)
    warped_nobg = align_face_affine(nobg_src, (405, 460), (588, 455))
    
    # Clean anatomical face gating:
    # Stop before 2D photo ears (X=320..704) so ONLY the 3D ears appear!
    w_arr = np.array(warped_nobg, dtype=np.float32)
    alpha = w_arr[:, :, 3] / 255.0
    
    # Gate X: X=320..704 with 25px smooth feather
    gate_x = np.clip((x_idx - 320.0) / 25.0, 0.0, 1.0) * np.clip((704.0 - x_idx) / 25.0, 0.0, 1.0)
    # Gate Y: rim_y down to chin (Y=640) fading smoothly to Y=675
    gate_y = np.clip((y_idx - (rim_y - 12.0)) / 18.0, 0.0, 1.0) * np.clip((675.0 - y_idx) / 35.0, 0.0, 1.0)
    face_alpha = alpha * gate_x * gate_y
    
    face_mask = Image.fromarray((face_alpha * 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(3.0))
    base.paste(Image.fromarray(w_arr[:, :, :3].astype(np.uint8)), (0, 0), face_mask)
    
    # Topi crown safety: Y < rim_y - 20 is 100% solid Topi
    solid_alpha = np.clip((rim_y - 20.0 - y_idx) / 6.0, 0.0, 1.0)
    solid_mask = Image.fromarray((solid_alpha * 255).astype(np.uint8), 'L')
    base.paste(topi_canvas, (0, 0), solid_mask)
    
    # Save preview and glTF texture
    base.save('preview_test_balen_v14.png')
    tex_path = 'test_balen_tex.png'
    gltf_img = base.transpose(Image.FLIP_TOP_BOTTOM)
    gltf_img.save(tex_path)
    print(f"Saved texture to {tex_path}")
    
    # Build GLB in Blender
    cmd = [
        BLENDER, '--background', '--python', 'build_nepali_blender_glb.py', '--',
        'balen_test', tex_path,
        '0.015', '0.015', '0.02',
        '0.015', '0.015', '0.02'
    ]
    subprocess.run(cmd, check=True)
    
    # Render all 4 angles
    for angle in ['front', 'side', 'back', 'three_quarter']:
        out_png = f'test_balen_v14_{angle}.png'
        subprocess.run([
            BLENDER, '--background', '--python', 'verify_render.py', '--',
            'public/models/balen_test.glb', out_png, angle
        ], check=True)
        print(f"Rendered {out_png}")

if __name__ == '__main__':
    build_test_balen()
