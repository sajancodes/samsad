import math
import os
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from procedural_head import (
    create_procedural_skin,
    create_natural_hair_texture,
    create_bhadgaunle_topi,
    create_dhaka_topi
)

def sample_skin_tone_from_face(face_img):
    """Samples realistic cheek/forehead skin tone directly from the politician portrait."""
    arr = np.array(face_img, dtype=np.float32)
    h, w, _ = arr.shape
    # Sample cheeks and forehead
    pts = [
        (int(h * 0.45), int(w * 0.38)), # Left cheek
        (int(h * 0.45), int(w * 0.62)), # Right cheek
        (int(h * 0.38), int(w * 0.50)), # Forehead/bridge
    ]
    samples = []
    for py, px in pts:
        if 0 <= py < h and 0 <= px < w:
            box = arr[max(0, py-10):min(h, py+10), max(0, px-10):min(w, px+10)]
            samples.append(box.mean(axis=(0, 1)))
    if samples:
        mean_rgb = np.mean(samples, axis=0)
        return (int(mean_rgb[0]), int(mean_rgb[1]), int(mean_rgb[2]))
    return (215, 178, 155)

def build_character_texture_v2(
    char_id,
    face_path,
    topi_type='bhadgaunle', # 'bhadgaunle', 'dhaka', or 'none'
    hair_type='black',      # 'black', 'salt_pepper', 'grey'
    skin_tone_rgb=None,     # Auto-sampled if None
    face_scale_factor=1.0,
    face_shift_y=0,
    face_radius_x=175.0,
    face_radius_y=170.0,
    topi_rim_front=285,
    topi_rim_back=380,
    hairline_y=320          # For non-topi characters
):
    print(f'Synthesizing 360° photorealistic V2 master texture for: {char_id}')
    width, height = 1024, 1024
    
    # Load Real Face Portrait
    face_src = Image.open(face_path).convert('RGB')
    if skin_tone_rgb is None:
        skin_tone_rgb = sample_skin_tone_from_face(face_src)
        print(f'  Auto-sampled skin tone from portrait: {skin_tone_rgb}')
    
    # 1. Base Anatomical Procedural Skin (Matching Portrait Skin Tone)
    skin_img = create_procedural_skin(width, height, base_rgb=skin_tone_rgb)
    
    # 2. Add Procedural Hair with Anatomical Hairline (Ears are Protected Skin)
    hair_img = create_natural_hair_texture(width, height, hair_type=hair_type)
    
    x_idx = np.arange(width)[None, :].astype(np.float32)
    y_idx = np.arange(height)[:, None].astype(np.float32)
    
    # Hair distribution mask:
    # Ears are at X = 200..265 (left) and X = 759..824 (right), Y = 380..520
    # Cheeks/Face are at X = 320..704, Y > rim_y
    # Hair exists on back of skull (X < 190 or X > 834) and above ears (Y < 400)
    
    # Calculate curved nape hairline on back of skull:
    # At back midline (X=0 and X=1024), nape hairline arches up to Y~530
    # Near ears (X~190 and X~834), nape hairline drops to Y~590
    back_dist = np.minimum(x_idx, 1024.0 - x_idx) # 0 at back midline, 512 at front
    nape_hairline_y = 530.0 + 60.0 * np.clip(back_dist / 220.0, 0.0, 1.0)
    
    # Fade at nape:
    nape_fade = np.clip((nape_hairline_y + 40.0 - y_idx) / 50.0, 0.0, 1.0)
    
    # Horizontal coverage:
    # Back of skull: back_dist < 185
    back_hair = np.clip((195.0 - back_dist) / 20.0, 0.0, 1.0)
    
    # Sideburns in front of ears (X ~ 275..315 and X ~ 709..749, Y ~ 360..480):
    sideburn_l = np.exp(-((x_idx - 295.0) / 20.0)**2) * np.clip((480.0 - y_idx) / 30.0, 0.0, 1.0)
    sideburn_r = np.exp(-((x_idx - 729.0) / 20.0)**2) * np.clip((480.0 - y_idx) / 30.0, 0.0, 1.0)
    sideburns = np.maximum(sideburn_l, sideburn_r)
    
    # Above-ear hair (Y < 400 around ears):
    above_ear = np.clip((410.0 - y_idx) / 30.0, 0.0, 1.0) * (
        np.clip((320.0 - x_idx) / 30.0, 0.0, 1.0) + np.clip((x_idx - 704.0) / 30.0, 0.0, 1.0)
    )
    
    if topi_type == 'none':
        # Full head hair: covers crown (Y < hairline_y) across entire width
        crown_hair = np.clip((hairline_y - y_idx) / 30.0, 0.0, 1.0)
        # Combine back hair, crown, above ear, sideburns
        hair_alpha_arr = np.maximum.reduce([
            back_hair * nape_fade,
            above_ear,
            crown_hair,
            sideburns * 0.8
        ])
    else:
        # Topi wearers: Hair starts at Topi rim
        rim_mid = (topi_rim_front + topi_rim_back) / 2.0
        rim_amp = (topi_rim_back - topi_rim_front) / 2.0
        rim_y = rim_mid - rim_amp * np.cos((x_idx - 512.0) / 512.0 * math.pi)
        
        # Below rim
        below_rim = np.clip((y_idx - (rim_y - 10.0)) / 15.0, 0.0, 1.0)
        hair_alpha_arr = np.maximum.reduce([
            back_hair * nape_fade,
            above_ear,
            sideburns * 0.8
        ]) * below_rim
        
    hair_mask = Image.fromarray((hair_alpha_arr * 255).astype(np.uint8), 'L')
    hair_mask = hair_mask.filter(ImageFilter.GaussianBlur(radius=3.0))
    skin_img.paste(hair_img, (0, 0), hair_mask)
    
    # 3. Add Authentic Nepali Topi (Covering 100% of upper skull)
    if topi_type != 'none':
        if topi_type == 'bhadgaunle':
            topi_canvas = create_bhadgaunle_topi(width, height)
        else: # dhaka
            topi_canvas = create_dhaka_topi(width, height)
            
        rim_mid = (topi_rim_front + topi_rim_back) / 2.0
        rim_amp = (topi_rim_back - topi_rim_front) / 2.0
        rim_y = rim_mid - rim_amp * np.cos((x_idx - 512.0) / 512.0 * math.pi)
        
        dist_to_rim = rim_y - y_idx
        topi_alpha = np.clip((dist_to_rim + 3.0) / 6.0, 0.0, 1.0)
        topi_mask = Image.fromarray((topi_alpha * 255).astype(np.uint8), 'L')
        skin_img.paste(topi_canvas, (0, 0), topi_mask)
        
        # 3D folded edge crease
        rim_crease = np.exp(-((dist_to_rim) / 3.0)**2) * 0.55
        base_arr = np.array(skin_img, dtype=np.float32)
        base_arr -= (rim_crease * 55.0)[:, :, None]
        skin_img = Image.fromarray(np.clip(base_arr, 0, 255).astype(np.uint8), 'RGB')
        
    # 4. Composite Real Face Portrait with Seamless Radial Feathering
    src_w, src_h = face_src.size
    scaled_w = int(src_w * face_scale_factor)
    scaled_h = int(src_h * face_scale_factor)
    face_scaled = face_src.resize((scaled_w, scaled_h), Image.LANCZOS)
    
    paste_x = 512 - scaled_w // 2
    paste_y = (height - scaled_h) // 2 + face_shift_y
    
    my, mx = np.ogrid[:scaled_h, :scaled_w]
    fcx = scaled_w / 2.0
    fcy = scaled_h * 0.485
    frx = face_radius_x * face_scale_factor
    fry = face_radius_y * face_scale_factor
    dist = ((mx - fcx) / frx)**2 + ((my - fcy) / fry)**2
    # Smooth Hermite/smoothstep feathering for seamless edge transition
    face_mask_arr = np.clip((1.0 - dist) * 2.8, 0.0, 1.0)
    
    # If wearing Topi, feather top boundary so Topi fabric stays 100% on top
    if topi_type != 'none':
        y_global = paste_y + my
        rim_at_x = rim_mid - rim_amp * np.cos((paste_x + mx - 512.0) / 512.0 * math.pi)
        topi_cut = np.clip((y_global - (rim_at_x - 6.0)) / 14.0, 0.0, 1.0)
        face_mask_arr *= topi_cut
        
    face_mask = Image.fromarray((face_mask_arr * 255).astype(np.uint8), 'L')
    face_mask = face_mask.filter(ImageFilter.GaussianBlur(radius=7.0))
    
    face_layer = Image.new('RGB', (width, height))
    face_alpha = Image.new('L', (width, height), 0)
    face_layer.paste(face_scaled, (paste_x, paste_y))
    face_alpha.paste(face_mask, (paste_x, paste_y))
    
    skin_img.paste(face_layer, (0, 0), face_alpha)
    
    # Solid Topi crown safety: ensure Y < rim_y - 25 is 100% solid Topi
    if topi_type != 'none':
        solid_alpha = np.clip((rim_y - 25.0 - y_idx) / 8.0, 0.0, 1.0)
        solid_mask = Image.fromarray((solid_alpha * 255).astype(np.uint8), 'L')
        skin_img.paste(topi_canvas, (0, 0), solid_mask)
        
    prev_path = f'preview_{char_id}_v2.png'
    skin_img.save(prev_path)
    print(f'Preview saved: {prev_path}')
    
    gltf_img = skin_img.transpose(Image.FLIP_TOP_BOTTOM)
    gltf_path = f'{char_id}_head_tex.png'
    gltf_img.save(gltf_path)
    print(f'glTF texture saved: {gltf_path}')
    return gltf_path
