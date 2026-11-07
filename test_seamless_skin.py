import numpy as np
from PIL import Image, ImageFilter
import cv2
import math

def build_seamless_head_texture(char_id, face_path, eyes, skin_rgb_hint, topi_type='none', hair_type='black'):
    w, h = 1024, 1024
    
    # 1. Load and align the character's 2D portrait
    src = Image.open(face_path).convert('RGBA')
    src_w, src_h = src.size
    
    # Target eye positions in upright UV space:
    # Left eye: (430, 365), Right eye: (594, 365) - eye distance = 164px
    t_lx, t_ly = 430.0, 365.0
    t_rx, t_ry = 594.0, 365.0
    
    s_lx, s_ly = float(eyes[0][0]), float(eyes[0][1])
    s_rx, s_ry = float(eyes[1][0]), float(eyes[1][1])
    
    # Compute similarity transform
    dx_s = s_rx - s_lx
    dy_s = s_ry - s_ly
    dist_s = math.sqrt(dx_s*dx_s + dy_s*dy_s)
    angle_s = math.atan2(dy_s, dx_s)
    
    dx_t = t_rx - t_lx
    dy_t = t_ry - t_ly
    dist_t = math.sqrt(dx_t*dx_t + dy_t*dy_t)
    angle_t = math.atan2(dy_t, dx_t)
    
    scale = dist_t / max(dist_s, 1.0)
    angle_deg = math.degrees(angle_s - angle_t)
    
    # Center of eyes
    center_s = ((s_lx + s_rx) * 0.5, (s_ly + s_ry) * 0.5)
    center_t = ((t_lx + t_rx) * 0.5, (t_ly + t_ry) * 0.5)
    
    M = cv2.getRotationMatrix2D(center_s, angle_deg, scale)
    M[0, 2] += (center_t[0] - center_s[0])
    M[1, 2] += (center_t[1] - center_s[1])
    
    src_np = np.array(src)
    warped_np = cv2.warpAffine(src_np, M, (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    
    # 2. Sample true skin tone from the aligned face
    # Sample from cheeks: left cheek (380, 420), right cheek (644, 420), forehead (512, 280)
    cheek_l = warped_np[400:440, 370:410, :3].mean(axis=(0, 1))
    cheek_r = warped_np[400:440, 614:654, :3].mean(axis=(0, 1))
    forehead = warped_np[260:300, 492:532, :3].mean(axis=(0, 1))
    
    # Blended representative skin tone
    true_skin = (cheek_l * 0.4 + cheek_r * 0.4 + forehead * 0.2)
    print(f"Sampled true skin for {char_id}: {true_skin}")
    
    # 3. Build Anatomical Shading & Ambient Occlusion from base_head_upright
    base = Image.open('base_head_upright.png').convert('RGB')
    base_arr = np.array(base, dtype=np.float32)
    
    # Clean beard / dark chin from base_arr to get pure anatomical form:
    # Chin/jaw region Y in [470, 680], X in [320, 704]
    # Replace the dark beard luminance with clean skin curvature
    base_lum = (base_arr[:, :, 0]*0.299 + base_arr[:, :, 1]*0.587 + base_arr[:, :, 2]*0.114)
    
    # Inpaint / smooth the beard zone in luminance
    y_grid, x_grid = np.ogrid[:h, :w]
    chin_dist = np.sqrt(((x_grid - 512.0) / 160.0)**2 + ((y_grid - 550.0) / 90.0)**2)
    is_beard_zone = (chin_dist < 1.0) & (base_lum < 130.0)
    
    clean_lum = base_lum.copy()
    clean_lum[is_beard_zone] = 145.0 - 25.0 * ((y_grid[is_beard_zone] - 470.0) / 150.0)
    
    # Blur clean_lum slightly to remove noise, preserve anatomical shapes
    clean_lum = cv2.GaussianBlur(clean_lum, (15, 15), 0)
    
    # Normalize shading relative to mid-cheek luminance (approx 150)
    norm_shading = np.clip(clean_lum / 150.0, 0.40, 1.15)
    
    # 4. Construct Full Anatomical Skin Canvas
    # Base skin = true_skin * anatomical shading
    skin_canvas = true_skin[None, None, :] * norm_shading[:, :, None]
    
    # Add subtle organic skin pore texture (high frequency grain)
    np.random.seed(42)
    pore_noise = np.random.normal(0, 2.5, (h, w, 1))
    skin_canvas = np.clip(skin_canvas + pore_noise, 0, 255)
    
    # 5. Build Ears from base_head_upright with exact color tinting
    # Ears are at X~230 and X~794, Y~420..500
    ear_l_dist = np.sqrt(((x_grid - 225.0) / 45.0)**2 + ((y_grid - 450.0) / 60.0)**2)
    ear_r_dist = np.sqrt(((x_grid - 799.0) / 45.0)**2 + ((y_grid - 450.0) / 60.0)**2)
    ear_mask = np.clip(1.0 - np.minimum(ear_l_dist, ear_r_dist), 0.0, 1.0)**2
    ear_mask = cv2.GaussianBlur(ear_mask, (9, 9), 0)
    
    ear_shading = np.clip(base_lum / 135.0, 0.45, 1.15)
    ear_rgb = true_skin[None, None, :] * ear_shading[:, :, None]
    # Tint ears with slight warm cartilage hue (+3 Red, -2 Blue)
    ear_rgb[:, :, 0] = np.clip(ear_rgb[:, :, 0] + 5.0, 0, 255)
    ear_rgb[:, :, 2] = np.clip(ear_rgb[:, :, 2] - 4.0, 0, 255)
    
    skin_canvas = skin_canvas * (1.0 - ear_mask[:, :, None]) + ear_rgb * ear_mask[:, :, None]
    
    # 6. Smooth Seamless Face Blending:
    # Instead of a hard trapezoid cutoff:
    # The face photo covers eyes, nose, mouth, cheeks, chin.
    # We create an elliptical anatomical face mask:
    # Center: (512, 420), Radius X: 195px, Radius Y: 180px
    face_rad = np.sqrt(((x_grid - 512.0) / 205.0)**2 + ((y_grid - 410.0) / 195.0)**2)
    
    # Smooth cosine transition over a wide 60-pixel zone
    raw_face_weight = np.clip((1.08 - face_rad) / 0.35, 0.0, 1.0)
    # Cosine S-curve for ultra smooth transition: 0.5 * (1 - cos(pi * w))
    face_weight = 0.5 * (1.0 - np.cos(raw_face_weight * math.pi))
    
    # Cut off clothes / collars below chin (Y > 640) smoothly
    neck_cutoff = np.clip((645.0 - y_grid) / 35.0, 0.0, 1.0)
    face_weight *= neck_cutoff
    
    # Gaussian blur mask to ensure zero sharp boundaries
    face_weight = cv2.GaussianBlur(face_weight, (31, 31), 0)
    
    # Color-harmonize the photo with the target skin canvas at the border:
    warped_rgb = warped_np[:, :, :3].astype(np.float32)
    
    # Composite face photo onto the anatomical skin canvas
    composite = skin_canvas * (1.0 - face_weight[:, :, None]) + warped_rgb * face_weight[:, :, None]
    
    # 7. Add Hair / Topi
    # Topi if present
    phi = (x_grid - 512.0) / 512.0 * math.pi
    if topi_type != 'none':
        from build_nepali_master_v5 import create_bhadgaunle_topi, create_dhaka_topi
        rim_y = 350.0 - 115.0 * np.cos(phi) + 12.0 * np.cos(2.0 * phi)
        if topi_type == 'bhadgaunle':
            topi_canvas = np.array(create_bhadgaunle_topi(w, h), dtype=np.float32)
        else:
            topi_canvas = np.array(create_dhaka_topi(w, h), dtype=np.float32)
            
        topi_alpha = np.clip((rim_y - y_grid + 2.0) / 4.0, 0.0, 1.0)
        topi_alpha = cv2.GaussianBlur(topi_alpha, (5, 5), 0)
        
        # 3D folded edge crease shadow
        dist_to_rim = rim_y - y_grid
        rim_crease = np.exp(-((dist_to_rim) / 3.0)**2) * 0.45
        composite -= (rim_crease * 45.0)[:, :, None]
        
        composite = composite * (1.0 - topi_alpha[:, :, None]) + topi_canvas * topi_alpha[:, :, None]
    else:
        # Full natural hair for non-topi characters
        from build_nepali_master_v5 import generate_anisotropic_hair
        hair_rgb = generate_anisotropic_hair(w, h, hair_type)
        
        # Hair covers:
        # Back and sides of head (distance from center > 240 for Y < 600)
        # Crown of head (Y < 235)
        # Forehead hairline: natural curved hairline
        back_dist = np.minimum(x_grid, 1024.0 - x_grid)
        sides_weight = np.clip((290.0 - back_dist) / 50.0, 0.0, 1.0)
        nape_fade = np.clip((610.0 - y_grid) / 50.0, 0.0, 1.0)
        
        # Forehead hairline curve: dips down at temples, peaks at center
        hairline_y = 230.0 + 35.0 * np.cos((x_grid - 512.0) / 180.0 * math.pi)
        hairline_mask = np.clip((hairline_y - y_grid) / 35.0, 0.0, 1.0)
        
        hair_mask = np.maximum(hairline_mask, sides_weight * nape_fade)
        # Don't cover ears
        hair_mask = hair_mask * (1.0 - ear_mask * 0.95)
        hair_mask = cv2.GaussianBlur(hair_mask, (15, 15), 0)
        
        composite = composite * (1.0 - hair_mask[:, :, None]) + hair_rgb * hair_mask[:, :, None]

    result = np.clip(composite, 0, 255).astype(np.uint8)
    img = Image.fromarray(result, 'RGB')
    img.save(f'preview_{char_id}_seamless.png')
    
    # Save glTF texture (flip top/bottom for glTF standard)
    gltf_img = img.transpose(Image.FLIP_TOP_BOTTOM)
    tex_path = f'{char_id}_head_seamless.png'
    gltf_img.save(tex_path)
    print(f"Generated seamless master texture: {tex_path}")
    return tex_path

if __name__ == '__main__':
    # Test on Durga Prasai
    build_seamless_head_texture(
        'durga',
        'public/faces/durga_hq.png',
        ((880, 375), (1070, 420)),
        (214, 172, 148),
        topi_type='none',
        hair_type='black'
    )
