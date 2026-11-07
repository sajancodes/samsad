import os
import math
import shutil
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

def create_bhadgaunle_topi(width=1024, height=1024):
    """Generates horizontally seamless authentic black Bhadgaunle woven fabric."""
    arr = np.zeros((height, width, 3), dtype=np.float32)
    # Authentic Bhadgaunle dark charcoal tone
    arr[:, :] = np.array([22.0, 22.0, 24.0])
    
    y = np.arange(height)[:, None]
    weave_h = np.sin(y * 1.6) * 3.5 + np.sin(y * 3.4) * 2.0
    
    # Horizontally periodic cross threads (loops at width 1024)
    x = np.arange(width)[None, :]
    weave_v = np.sin(x / 1024.0 * 2.0 * math.pi * 64.0) * 3.0 + np.sin(x / 1024.0 * 2.0 * math.pi * 128.0) * 1.5
    
    # Subtle anatomical light highlight across the crown
    fold_light = np.cos(x / 1024.0 * 2.0 * math.pi) * 3.0
    
    np.random.seed(101)
    noise = np.random.normal(0, 1.2, (height, width, 3))
    
    arr = arr + weave_h[:, :, None] + weave_v[:, :, None] + fold_light[:, :, None] + noise
    arr = np.clip(arr, 12, 42).astype(np.uint8)
    return Image.fromarray(arr, 'RGB')

def create_dhaka_topi(width=1024, height=1024):
    """Generates horizontally seamless authentic Nepali Dhaka geometric pattern."""
    im = Image.new('RGB', (width, height), (35, 18, 20))
    draw = ImageDraw.Draw(im)
    
    dw, dh = 32, 32
    for y in range(0, height, dh):
        for x in range(0, width, dw):
            col_idx = ((x // dw) + (y // dh)) % 4
            if col_idx == 0:
                col = (145, 30, 36) # Crimson
            elif col_idx == 1:
                col = (28, 28, 32)  # Charcoal
            elif col_idx == 2:
                col = (195, 148, 55) # Ochre Gold
            else:
                col = (38, 80, 48)   # Forest Green
            
            cx, cy = x + dw//2, y + dh//2
            pts = [(cx, y), (x + dw, cy), (cx, y + dh), (x, cy)]
            draw.polygon(pts, fill=col)
            
            pts_inner = [(cx, y + dh//4), (x + 3*dw//4, cy), (cx, y + 3*dh//4), (x + dw//4, cy)]
            draw.polygon(pts_inner, fill=(col[0]//2, col[1]//2, col[2]//2))
            
    im = im.filter(ImageFilter.GaussianBlur(radius=0.7))
    return im

def build_head_texture(
    char_id,
    face_path,
    topi_type='bhadgaunle', # 'bhadgaunle', 'dhaka', or 'none'
    hair_type='black',      # 'black', 'salt_pepper', 'grey'
    skin_tone_mult=(1.0, 1.0, 1.0),
    face_scale_factor=1.0,
    face_shift_y=0,
    face_radius_x=175.0,
    face_radius_y=165.0,
    topi_rim_front=285,
    topi_rim_back=365
):
    print(f'Synthesizing 360° master texture for: {char_id}')
    width, height = 1024, 1024
    
    # 1. Base Anatomical Unwrapped Head (Rahul base with real ears, neck, occipital)
    base = Image.open('base_head_upright.png').convert('RGB')
    base_arr = np.array(base, dtype=np.float32)
    
    # Skin tone tinting
    base_arr[:, :, 0] *= skin_tone_mult[0]
    base_arr[:, :, 1] *= skin_tone_mult[1]
    base_arr[:, :, 2] *= skin_tone_mult[2]
    
    # Hair tinting on sides and back with smooth vertical transition into neck
    x_idx = np.arange(width)[None, :]
    y_idx = np.arange(height)[:, None]
    
    # Sides & back hair horizontal weight (1.0 on sides and back, 0.0 on face)
    horiz_hair = np.zeros((1, width), dtype=np.float32)
    horiz_hair[0, :260] = 1.0
    horiz_hair[0, 260:340] = np.linspace(1.0, 0.0, 80)
    horiz_hair[0, 684:764] = np.linspace(0.0, 1.0, 80)
    horiz_hair[0, 764:] = 1.0
    
    # Smooth vertical fade out from head into neck skin (no hard horizontal lines)
    vert_hair = np.clip((600.0 - y_idx) / 100.0, 0.0, 1.0)
    hair_blend_weight = (horiz_hair * vert_hair)[:, :, None]
    
    if hair_type == 'black':
        target_hair = base_arr * 0.22 + 6.0
    elif hair_type == 'salt_pepper':
        lum = base_arr[:, :, 0]*0.299 + base_arr[:, :, 1]*0.587 + base_arr[:, :, 2]*0.114
        target_hair = np.zeros_like(base_arr)
        target_hair[:, :, 0] = lum * 0.75 + 22.0
        target_hair[:, :, 1] = lum * 0.75 + 22.0
        target_hair[:, :, 2] = lum * 0.78 + 24.0
    elif hair_type == 'grey':
        lum = base_arr[:, :, 0]*0.299 + base_arr[:, :, 1]*0.587 + base_arr[:, :, 2]*0.114
        target_hair = np.zeros_like(base_arr)
        target_hair[:, :, 0] = lum * 0.95 + 45.0
        target_hair[:, :, 1] = lum * 0.95 + 45.0
        target_hair[:, :, 2] = lum * 1.00 + 48.0

    # Smoothly blend target hair color with original
    base_arr = base_arr * (1.0 - hair_blend_weight) + target_hair * hair_blend_weight
    base = Image.fromarray(np.clip(base_arr, 0, 255).astype(np.uint8), 'RGB')
    
    # 2. Add Topi (if character wears Topi)
    if topi_type != 'none':
        rim_mid = (topi_rim_front + topi_rim_back) / 2.0
        rim_amp = (topi_rim_back - topi_rim_front) / 2.0
        # Periodic rim curve connecting front brow to back skull seamlessly
        rim_y = rim_mid - rim_amp * np.cos((x_idx - 512.0) / 512.0 * math.pi)
        
        if topi_type == 'bhadgaunle':
            topi_img = create_bhadgaunle_topi(width, height)
        else: # dhaka
            topi_img = create_dhaka_topi(width, height)
            
        dist_to_rim = rim_y - y_idx
        topi_alpha = np.clip((dist_to_rim + 2.0) / 4.0, 0.0, 1.0)
        topi_mask = Image.fromarray((topi_alpha * 255).astype(np.uint8), 'L')
        
        base.paste(topi_img, (0, 0), topi_mask)
        
        # Add rim fold shadow crease
        rim_crease = np.exp(-((dist_to_rim) / 2.5)**2) * 0.45
        b_arr = np.array(base, dtype=np.float32)
        b_arr -= (rim_crease * 45.0)[:, :, None]
        base = Image.fromarray(np.clip(b_arr, 0, 255).astype(np.uint8), 'RGB')

    # 3. Composite Real Face Portrait
    face_src = Image.open(face_path).convert('RGB')
    src_w, src_h = face_src.size
    
    scaled_w = int(src_w * face_scale_factor)
    scaled_h = int(src_h * face_scale_factor)
    face_scaled = face_src.resize((scaled_w, scaled_h), Image.LANCZOS)
    
    # Center face at X=512
    paste_x = 512 - scaled_w // 2
    paste_y = (height - scaled_h) // 2 + face_shift_y
    
    # Create smooth radial face mask
    my, mx = np.ogrid[:scaled_h, :scaled_w]
    fcx = scaled_w / 2.0
    fcy = scaled_h * 0.485
    frx = face_radius_x * face_scale_factor
    fry = face_radius_y * face_scale_factor
    dist = ((mx - fcx) / frx)**2 + ((my - fcy) / fry)**2
    face_mask_arr = np.clip((1.0 - dist) * 3.5, 0.0, 1.0)
    
    # If character wears Topi, feather the top so Topi fabric stays 100% on top of cranium
    if topi_type != 'none':
        y_global = paste_y + my
        rim_at_x = rim_mid - rim_amp * np.cos((paste_x + mx - 512.0) / 512.0 * math.pi)
        topi_cut = np.clip((y_global - (rim_at_x - 8.0)) / 16.0, 0.0, 1.0)
        face_mask_arr *= topi_cut
        
    face_mask = Image.fromarray((face_mask_arr * 255).astype(np.uint8), 'L')
    face_mask = face_mask.filter(ImageFilter.GaussianBlur(radius=5.0))
    
    # Paste face onto base
    face_layer = Image.new('RGB', (width, height))
    face_alpha = Image.new('L', (width, height), 0)
    face_layer.paste(face_scaled, (paste_x, paste_y))
    face_alpha.paste(face_mask, (paste_x, paste_y))
    
    base.paste(face_layer, (0, 0), face_alpha)
    
    # Ensure upper crown (Y < rim_y - 20) is 100% solid Topi
    if topi_type != 'none':
        solid_alpha = np.clip((rim_y - 20.0 - y_idx) / 8.0, 0.0, 1.0)
        solid_mask = Image.fromarray((solid_alpha * 255).astype(np.uint8), 'L')
        solid_mask = solid_mask.filter(ImageFilter.GaussianBlur(radius=2.0))
        base.paste(topi_img, (0, 0), solid_mask)
        
    # Save preview
    prev_path = f'preview_{char_id}_360.png'
    base.save(prev_path)
    print(f'Preview saved: {prev_path}')
    
    # Convert to glTF UV space (vertical flip)
    gltf_img = base.transpose(Image.FLIP_TOP_BOTTOM)
    gltf_path = f'{char_id}_head_tex.png'
    gltf_img.save(gltf_path)
    print(f'glTF texture saved: {gltf_path}')
    return gltf_path
