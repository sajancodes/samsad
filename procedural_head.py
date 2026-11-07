import math
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

def create_procedural_skin(width=1024, height=1024, base_rgb=(215, 178, 155)):
    """Creates smooth, natural human skin base with subtle anatomical shading and pore micro-texture."""
    r, g, b = base_rgb
    arr = np.zeros((height, width, 3), dtype=np.float32)
    arr[:, :, 0] = r
    arr[:, :, 1] = g
    arr[:, :, 2] = b
    
    y = np.arange(height)[:, None].astype(np.float32)
    x = np.arange(width)[None, :].astype(np.float32)
    
    # Subtle anatomical neck shading:
    # Jaw shadow around Y=620..680 in front (X ~ 350..674)
    front_weight = np.clip(1.0 - np.abs(x - 512.0) / 190.0, 0.0, 1.0)
    jaw_shadow = np.exp(-((y - 640.0) / 45.0)**2) * 16.0 * front_weight
    
    # Nape shadow on back neck around Y=560..700
    back_dist = np.minimum(x, 1024.0 - x)
    back_weight = np.clip(1.0 - back_dist / 220.0, 0.0, 1.0)
    nape_shadow = np.exp(-((y - 580.0) / 60.0)**2) * 14.0 * back_weight
    
    # Neck muscle contours (Sternocleidomastoid)
    neck_grad = np.clip((y - 620.0) / 404.0, 0.0, 1.0) * 10.0
    
    total_shadow = jaw_shadow + nape_shadow + neck_grad
    arr[:, :, 0] -= total_shadow * 1.0
    arr[:, :, 1] -= total_shadow * 1.15
    arr[:, :, 2] -= total_shadow * 1.25
    
    # Subtle skin pore micro-texture
    np.random.seed(42)
    noise = np.random.normal(0, 1.5, (height, width, 3))
    arr += noise
    
    arr = np.clip(arr, 10, 255).astype(np.uint8)
    return Image.fromarray(arr, 'RGB')

def create_natural_hair_texture(width=1024, height=1024, hair_type='black'):
    """Creates realistic fine-grain directional combed hair with natural strand variation."""
    arr = np.zeros((height, width, 3), dtype=np.float32)
    
    x = np.arange(width)[None, :].astype(np.float32)
    y = np.arange(height)[:, None].astype(np.float32)
    
    # Fine directional strands: high-frequency horizontal variation stretched vertically
    # Using integer harmonics across 1024 for horizontal continuity
    fine_strands = (
        np.sin(x / 1024.0 * 2.0 * math.pi * 512.0) * 2.5 +
        np.sin(x / 1024.0 * 2.0 * math.pi * 256.0 + y * 0.04) * 3.5 +
        np.sin(x / 1024.0 * 2.0 * math.pi * 128.0 - y * 0.02) * 4.0 +
        np.cos(x / 1024.0 * 2.0 * math.pi * 64.0) * 3.0
    )
    
    # Subtle anatomical sheen highlight
    sheen = np.exp(-((y - 480.0) / 70.0)**2) * 8.0
    
    np.random.seed(101)
    noise = np.random.normal(0, 1.8, (height, width, 3))
    
    if hair_type == 'black':
        base_col = np.array([20.0, 20.0, 22.0])
        strand_col = fine_strands[:, :, None] * 0.7
        arr[:, :] = base_col + strand_col + (sheen * 0.4)[:, :, None] + noise
    elif hair_type == 'salt_pepper':
        base_col = np.array([48.0, 50.0, 54.0])
        # Fine silver strands
        silver_waves = (
            np.sin(x / 1024.0 * 2.0 * math.pi * 384.0 + y * 0.03) * 0.5 +
            np.sin(x / 1024.0 * 2.0 * math.pi * 192.0) * 0.5
        )
        silver_mask = np.clip((silver_waves - 0.2) * 3.0, 0.0, 1.0)
        silver_strands = (silver_mask * 42.0)[:, :, None]
        strand_col = fine_strands[:, :, None] * 1.0
        arr[:, :] = base_col + strand_col + silver_strands + (sheen * 0.8)[:, :, None] + noise
    elif hair_type == 'grey':
        base_col = np.array([115.0, 118.0, 122.0])
        silver_waves = np.sin(x / 1024.0 * 2.0 * math.pi * 256.0 + y * 0.02)
        silver_mask = np.clip((silver_waves + 0.1) * 2.0, 0.0, 1.0)
        silver_strands = (silver_mask * 38.0)[:, :, None]
        strand_col = fine_strands[:, :, None] * 1.2
        arr[:, :] = base_col + strand_col + silver_strands + (sheen * 1.0)[:, :, None] + noise
        
    arr = np.clip(arr, 5, 245).astype(np.uint8)
    return Image.fromarray(arr, 'RGB').filter(ImageFilter.GaussianBlur(radius=0.5))

def create_bhadgaunle_topi(width=1024, height=1024):
    """Generates rich, horizontally seamless authentic black Bhadgaunle woven fabric."""
    arr = np.zeros((height, width, 3), dtype=np.float32)
    # Authentic Bhadgaunle deep woven tone
    arr[:, :] = np.array([28.0, 28.0, 30.0])
    
    y = np.arange(height)[:, None].astype(np.float32)
    x = np.arange(width)[None, :].astype(np.float32)
    
    # Diamond twill micro-weave (cross threads)
    weave_1 = np.sin((x + y) / 1024.0 * 2.0 * math.pi * 128.0) * 3.5
    weave_2 = np.sin((x - y) / 1024.0 * 2.0 * math.pi * 128.0) * 3.5
    
    # Subtle natural crease
    fold = np.cos(x / 1024.0 * 2.0 * math.pi * 2.0) * 2.5
    
    np.random.seed(123)
    noise = np.random.normal(0, 1.2, (height, width, 3))
    
    arr = arr + weave_1[:, :, None] + weave_2[:, :, None] + fold[:, :, None] + noise
    arr = np.clip(arr, 15, 48).astype(np.uint8)
    return Image.fromarray(arr, 'RGB')

def create_dhaka_topi(width=1024, height=1024):
    """Generates rich, horizontally seamless authentic Nepali Dhaka geometric pattern."""
    im = Image.new('RGB', (width, height), (38, 18, 22))
    draw = ImageDraw.Draw(im)
    
    dw, dh = 32, 32
    for y in range(0, height, dh):
        for x in range(0, width, dw):
            col_idx = ((x // dw) + (y // dh)) % 4
            if col_idx == 0:
                col = (165, 34, 42)   # Rich Crimson
            elif col_idx == 1:
                col = (28, 30, 34)    # Charcoal
            elif col_idx == 2:
                col = (215, 162, 60)  # Ochre Gold
            else:
                col = (38, 92, 54)    # Emerald Green
            
            cx, cy = x + dw//2, y + dh//2
            pts = [(cx, y), (x + dw, cy), (cx, y + dh), (x, cy)]
            draw.polygon(pts, fill=col)
            
            pts_inner = [(cx, y + dh//4), (x + 3*dw//4, cy), (cx, y + 3*dh//4), (x + dw//4, cy)]
            draw.polygon(pts_inner, fill=(col[0]//2, col[1]//2, col[2]//2))
            
    return im.filter(ImageFilter.GaussianBlur(radius=0.7))
