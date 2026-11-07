import numpy as np
from PIL import Image, ImageFilter
import math

def create_real_balen_texture():
    w, h = 1024, 1024
    
    # 1. Load the authentic 1024x1024 studio photo of Balen
    src = Image.open('public/faces/balen.webp').convert('RGBA')
    
    # Balen's eyes in balen.webp: (405, 460) and (588, 455)
    s_lx, s_ly = 405.0, 460.0
    s_rx, s_ry = 588.0, 455.0
    
    # Target in 1024x1024 upright UV space:
    t_lx, t_ly = 420.0, 335.0
    t_rx, t_ry = 604.0, 335.0
    
    # Compute affine transformation
    dx_s = s_rx - s_lx
    dy_s = s_ry - s_ly
    dist_s = math.sqrt(dx_s*dx_s + dy_s*dy_s) # 183.07
    angle_s = math.atan2(dy_s, dx_s)
    
    dx_t = t_rx - t_lx
    dy_t = t_ry - t_ly
    dist_t = math.sqrt(dx_t*dx_t + dy_t*dy_t) # 184.0
    angle_t = math.atan2(dy_t, dx_t)
    
    scale = dist_t / dist_s
    angle = angle_t - angle_s
    
    cx_s = (s_lx + s_rx) * 0.5
    cy_s = (s_ly + s_ry) * 0.5
    cx_t = (t_lx + t_rx) * 0.5
    cy_t = (t_ly + t_ry) * 0.5
    
    # Transformation matrix for PIL:
    # [x_s] = [ cos  sin] [x_t - cx_t] / scale + [cx_s]
    # [y_s]   [-sin  cos] [y_t - cy_t] / scale   [cy_s]
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    a = cos_a / scale
    b = sin_a / scale
    c = cx_s - a * cx_t - b * cy_t
    d = -sin_a / scale
    e = cos_a / scale
    f = cy_s - d * cx_t - e * cy_t
    
    warped_photo = src.transform((w, h), Image.AFFINE, (a, b, c, d, e, f), resample=Image.BICUBIC)
    w_arr = np.array(warped_photo, dtype=np.float32)
    
    # 2. Build full 360 base canvas with authentic skin & Bhadgaunle Topi
    # Sample true skin from Balen's cheeks (X=350, Y=430) and (X=670, Y=430)
    skin_col = w_arr[410:450, 340:370, :3].mean(axis=(0, 1))
    print('Sampled Balen skin color:', skin_col)
    
    # Base canvas
    base = Image.new('RGB', (w, h), (int(skin_col[0]), int(skin_col[1]), int(skin_col[2])))
    b_arr = np.array(base, dtype=np.float32)
    
    y_idx = np.arange(h, dtype=np.float32)[:, None]
    x_idx = np.arange(w, dtype=np.float32)[None, :]
    
    # 3. Authentic Bhadgaunle Topi across top & cranium (Y < 260)
    # Periodic rim curve
    phi = (x_idx - 512.0) / 512.0 * math.pi
    rim_y = 265.0 - 55.0 * np.cos(phi)
    
    from build_nepali_master_v5 import create_bhadgaunle_topi, generate_anisotropic_hair
    topi_canvas = np.array(create_bhadgaunle_topi(w, h), dtype=np.float32)
    
    # Hair for sides and back
    hair_rgb = generate_anisotropic_hair(w, h, 'black')
    back_dist = np.minimum(x_idx, 1024.0 - x_idx)
    nape_fade = np.clip((620.0 - y_idx) / 50.0, 0.0, 1.0)
    sides_weight = np.clip((300.0 - back_dist) / 50.0, 0.0, 1.0) * nape_fade
    
    b_arr = b_arr * (1.0 - sides_weight[:, :, None]) + hair_rgb * sides_weight[:, :, None]
    
    # Clean sculpted ears from base_head_upright
    base_ear = Image.open('base_head_upright.png').convert('RGB')
    ear_arr = np.array(base_ear, dtype=np.float32)
    ear_lum = (ear_arr[:, :, 0]*0.299 + ear_arr[:, :, 1]*0.587 + ear_arr[:, :, 2]*0.114) / 140.0
    ear_col = skin_col[None, None, :] * np.clip(ear_lum[:, :, None], 0.45, 1.15)
    
    dist_l = np.sqrt(((x_idx - 225.0) / 45.0)**2 + ((y_idx - 440.0) / 60.0)**2)
    dist_r = np.sqrt(((x_idx - 799.0) / 45.0)**2 + ((y_idx - 440.0) / 60.0)**2)
    ear_mask = np.clip(1.0 - np.minimum(dist_l, dist_r), 0.0, 1.0)**2
    
    b_arr = b_arr * (1.0 - ear_mask[:, :, None]) + ear_col * ear_mask[:, :, None]
    
    # Topi covers cranium
    topi_mask = np.clip((rim_y - y_idx) / 4.0, 0.0, 1.0)
    b_arr = b_arr * (1.0 - topi_mask[:, :, None]) + topi_canvas * topi_mask[:, :, None]
    
    # 4. Composite Balen's Real Face Photo Seamlessly
    # The photo contains: Topi, Sunglasses, Nose, Lips, Beard, Cheeks
    # We blend it over the face region using a smooth anatomical feather
    dx = np.abs(x_idx - 512.0)
    # Face width: 220px at eyes (Y=335), tapering to 140px at chin (Y=620)
    jaw_prog = np.clip((y_idx - 335.0) / 285.0, 0.0, 1.0)
    allowed_w = 230.0 * (1.0 - 0.35 * jaw_prog)
    
    # Smooth cosine horizontal transition
    feather_w = 40.0
    gate_x = np.clip((allowed_w - dx) / feather_w, 0.0, 1.0)
    gate_x = 0.5 * (1.0 - np.cos(gate_x * math.pi))
    
    # Vertical bounds:
    # Top: starts above the sunglasses (Y = 240) into the Topi
    # Bottom: ends below chin (Y = 645)
    gate_top = np.clip((y_idx - 220.0) / 30.0, 0.0, 1.0)
    gate_bot = np.clip((650.0 - y_idx) / 35.0, 0.0, 1.0)
    face_mask = gate_x * gate_top * gate_bot
    
    # Gaussian blur the blend mask
    mask_im = Image.fromarray((face_mask * 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(8.0))
    face_alpha = np.array(mask_im, dtype=np.float32) / 255.0
    
    # Final composite
    final_arr = b_arr * (1.0 - face_alpha[:, :, None]) + w_arr[:, :, :3] * face_alpha[:, :, None]
    
    # Ensure solid Bhadgaunle topi above Y < 210
    solid_topi_mask = np.clip((210.0 - y_idx) / 10.0, 0.0, 1.0)
    final_arr = final_arr * (1.0 - solid_topi_mask[:, :, None]) + topi_canvas * solid_topi_mask[:, :, None]
    
    res = Image.fromarray(np.clip(final_arr, 0, 255).astype(np.uint8), 'RGB')
    res.save('balen_real_master_upright.png')
    res.transpose(Image.FLIP_TOP_BOTTOM).save('balen_real_master_gltf.png')
    print('Generated authentic real photo Balen texture: balen_real_master_gltf.png')

if __name__ == '__main__':
    create_real_balen_texture()
