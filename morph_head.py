import bpy
import numpy as np

def apply_skull_morph(obj, char_id):
    mesh = obj.data
    verts = mesh.vertices
    
    # Coordinates array
    coords = np.array([v.co for v in verts])
    orig_coords = coords.copy()
    
    # Z ranges:
    # Top of head: Z > 1.72
    # Eyes/brow: Z in [1.66, 1.72]
    # Cheeks/zygoma: Z in [1.60, 1.68]
    # Mouth/lips: Z in [1.58, 1.63], |X| < 0.035, Y < -0.10
    # Lower jaw/jowls: Z in [1.52, 1.61]
    # Chin: Z in [1.53, 1.58], Y < -0.08
    # Double chin / submental: Z in [1.50, 1.55], Y in [-0.07, 0.00]
    # Neck: Z in [1.48, 1.54]
    
    xs = coords[:, 0]
    ys = coords[:, 1]
    zs = coords[:, 2]
    
    # Protect eyes and inner mouth from distortion
    is_eye_zone = (np.abs(xs) < 0.055) & (zs > 1.65) & (zs < 1.71) & (ys < -0.07)
    is_mouth_zone = (np.abs(xs) < 0.032) & (zs > 1.58) & (zs < 1.64) & (ys < -0.10)
    protected = is_eye_zone | is_mouth_zone
    
    if char_id in ['durga', 'kpoli']: # Heavy-set, chubby, round, fleshy jowls
        # 1. Broaden mid-to-lower cheeks and jowls
        jowl_weight = np.clip((zs - 1.50) / 0.06, 0.0, 1.0) * np.clip((1.68 - zs) / 0.08, 0.0, 1.0)
        # Wider lateral expansion
        scale_x = 1.0 + (0.13 if char_id == 'durga' else 0.10) * jowl_weight * np.clip((np.abs(xs) - 0.02) / 0.04, 0.0, 1.0)
        xs *= scale_x
        
        # 2. Plump cheek projection forward
        cheek_weight = np.clip((zs - 1.57) / 0.05, 0.0, 1.0) * np.clip((1.67 - zs) / 0.05, 0.0, 1.0)
        cheek_mask = cheek_weight * (np.abs(xs) > 0.03) * (ys < -0.04)
        ys -= 0.007 * cheek_mask # Move forward
        
        # 3. Double chin / submental fullness
        double_chin_weight = np.clip((zs - 1.49) / 0.04, 0.0, 1.0) * np.clip((1.56 - zs) / 0.04, 0.0, 1.0)
        submental_mask = double_chin_weight * (ys > -0.08) * (ys < 0.01) * (np.abs(xs) < 0.055)
        ys -= 0.010 * submental_mask # Push submental fat forward
        zs -= 0.004 * submental_mask # Sag slightly
        
        # 4. Thicker neck
        neck_weight = np.clip((1.54 - zs) / 0.06, 0.0, 1.0)
        xs *= (1.0 + 0.11 * neck_weight)
        ys *= (1.0 + 0.08 * neck_weight)
        
    elif char_id == 'deuba': # Heavy elderly sagging jowls, thick neck, receding soft chin
        # 1. Sagging lower jowls
        jowl_weight = np.clip((zs - 1.51) / 0.05, 0.0, 1.0) * np.clip((1.63 - zs) / 0.06, 0.0, 1.0)
        scale_x = 1.0 + 0.14 * jowl_weight * np.clip((np.abs(xs) - 0.025) / 0.04, 0.0, 1.0)
        xs *= scale_x
        zs -= 0.005 * jowl_weight * (np.abs(xs) > 0.035) # Jowl droop
        
        # 2. Receding soft chin
        chin_mask = (zs > 1.52) & (zs < 1.58) & (ys < -0.07) & (np.abs(xs) < 0.035)
        ys += 0.006 * chin_mask # Pull chin back
        
        # 3. Heavy elderly neck
        neck_weight = np.clip((1.54 - zs) / 0.06, 0.0, 1.0)
        xs *= (1.0 + 0.13 * neck_weight)
        ys *= (1.0 + 0.10 * neck_weight)
        
    elif char_id == 'balen': # Broad square masculine jaw, strong forward chin, tall cranium
        # 1. Wide angular mandibular corners
        jaw_corner_weight = np.clip((zs - 1.53) / 0.04, 0.0, 1.0) * np.clip((1.63 - zs) / 0.05, 0.0, 1.0)
        jaw_mask = jaw_corner_weight * (np.abs(xs) > 0.04) * (ys > -0.07) * (ys < 0.02)
        xs *= (1.0 + 0.11 * jaw_mask)
        
        # 2. Strong prominent forward-thrust chin
        chin_mask = np.clip((zs - 1.53) / 0.03, 0.0, 1.0) * np.clip((1.58 - zs) / 0.03, 0.0, 1.0) * (ys < -0.07) * (np.abs(xs) < 0.03)
        ys -= 0.008 * chin_mask # Push chin forward
        
        # 3. Squarer chin base (broaden chin tip)
        xs *= (1.0 + 0.07 * chin_mask)
        
        # 4. Taller cranium
        cranium_weight = np.clip((zs - 1.70) / 0.10, 0.0, 1.0)
        zs += 0.007 * cranium_weight
        
    elif char_id == 'harka': # Compact Kirat face, high prominent cheekbones, flatter profile
        # 1. High prominent cheekbones (lateral projection)
        cheekbone_weight = np.clip((zs - 1.62) / 0.04, 0.0, 1.0) * np.clip((1.70 - zs) / 0.04, 0.0, 1.0)
        zygoma_mask = cheekbone_weight * (np.abs(xs) > 0.035) * (ys < 0.0)
        xs *= (1.0 + 0.10 * zygoma_mask)
        
        # 2. Compact facial height (shorten lower face)
        mid_lower = np.clip((zs - 1.52) / 0.06, 0.0, 1.0) * np.clip((1.66 - zs) / 0.06, 0.0, 1.0)
        zs += (1.60 - zs) * 0.07 * mid_lower
        
        # 3. Flatter nasal/anterior projection
        ant_mask = (ys < -0.08) * (zs > 1.60) * (zs < 1.70)
        ys += 0.004 * ant_mask
        
    elif char_id == 'gagan': # Lean, thin, narrow triangular face, sharp chin, slender neck
        # 1. Narrow cheeks and mid-face
        lean_weight = np.clip((zs - 1.52) / 0.05, 0.0, 1.0) * np.clip((1.69 - zs) / 0.06, 0.0, 1.0)
        xs *= (1.0 - 0.08 * lean_weight)
        
        # 2. Sharp tapered chin
        chin_weight = np.clip((zs - 1.53) / 0.03, 0.0, 1.0) * np.clip((1.58 - zs) / 0.03, 0.0, 1.0)
        xs *= (1.0 - 0.10 * chin_weight)
        ys -= 0.004 * chin_weight * (ys < -0.07) # Sharp forward tip
        
        # 3. Slender neck
        neck_weight = np.clip((1.54 - zs) / 0.06, 0.0, 1.0)
        xs *= (1.0 - 0.08 * neck_weight)
        ys *= (1.0 - 0.07 * neck_weight)
        
    elif char_id == 'prachanda': # Sturdy, broad square jaw, heavy brow
        # 1. Wide mandibular structure
        jaw_weight = np.clip((zs - 1.53) / 0.04, 0.0, 1.0) * np.clip((1.64 - zs) / 0.05, 0.0, 1.0)
        xs *= (1.0 + 0.09 * jaw_weight * np.clip((np.abs(xs) - 0.02) / 0.04, 0.0, 1.0))
        # 2. Solid broad chin
        chin_mask = (zs > 1.53) & (zs < 1.58) & (ys < -0.07)
        xs *= (1.0 + 0.06 * chin_mask)
        
    elif char_id == 'genz': # Stylized V-line jaw, anime/cyber aesthetic
        # 1. Sharp V-taper from cheeks down to chin
        v_weight = np.clip((1.63 - zs) / 0.10, 0.0, 1.0)
        xs *= (1.0 - 0.12 * v_weight)
        
        # 2. High sleek cheekbones
        cb_weight = np.clip((zs - 1.63) / 0.04, 0.0, 1.0) * np.clip((1.70 - zs) / 0.04, 0.0, 1.0)
        xs *= (1.0 + 0.03 * cb_weight * (np.abs(xs) > 0.04))
        
        # 3. Slim cyber neck
        neck_weight = np.clip((1.54 - zs) / 0.06, 0.0, 1.0)
        xs *= (1.0 - 0.11 * neck_weight)
        ys *= (1.0 - 0.10 * neck_weight)

    # Re-apply protection to mouth & eye holes
    xs[protected] = orig_coords[:, 0][protected]
    ys[protected] = orig_coords[:, 1][protected]
    zs[protected] = orig_coords[:, 2][protected]
    
    # Assign back to mesh vertices
    for i, v in enumerate(verts):
        v.co.x = xs[i]
        v.co.y = ys[i]
        v.co.z = zs[i]
        
    mesh.update()
    print(f"Applied 3D skull morphology for {char_id.upper()}!")
