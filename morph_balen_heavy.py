import bpy
import numpy as np

def morph_balen_heavy():
    # 1. Morph Head Mesh
    head = bpy.data.objects.get('Head')
    if head:
        coords = np.array([v.co for v in head.data.vertices])
        orig = coords.copy()
        
        xs = coords[:, 0]
        ys = coords[:, 1]
        zs = coords[:, 2]
        
        # Eyes / mouth protection
        is_eye = (np.abs(xs) < 0.055) & (zs > 1.65) & (zs < 1.71) & (ys < -0.07)
        is_mouth = (np.abs(xs) < 0.032) & (zs > 1.58) & (zs < 1.64) & (ys < -0.10)
        protected = is_eye | is_mouth
        
        # A. Bigger, deeper cranium (top and back of head)
        # Deepen occiput (back of head):
        back_mask = np.clip((ys - 0.0) / 0.06, 0.0, 1.0) * np.clip((zs - 1.52) / 0.10, 0.0, 1.0)
        ys += 0.022 * back_mask # Push back of skull out backwards
        
        # B. Taller skull dome
        cranium_mask = np.clip((zs - 1.68) / 0.12, 0.0, 1.0)
        zs += 0.018 * cranium_mask
        xs *= (1.0 + 0.09 * cranium_mask)
        
        # C. Broad masculine square jaw (mandibular angles)
        jaw_weight = np.clip((zs - 1.52) / 0.04, 0.0, 1.0) * np.clip((1.64 - zs) / 0.05, 0.0, 1.0)
        jaw_lateral = jaw_weight * np.clip((np.abs(xs) - 0.025) / 0.04, 0.0, 1.0)
        xs *= (1.0 + 0.15 * jaw_lateral)
        
        # D. Strong forward-thrust chin
        chin_mask = np.clip((zs - 1.52) / 0.03, 0.0, 1.0) * np.clip((1.59 - zs) / 0.03, 0.0, 1.0) * (ys < -0.065)
        ys -= 0.010 * chin_mask # Push chin forward
        xs *= (1.0 + 0.08 * chin_mask) # Squarer chin
        
        # E. Massive thick neck
        neck_weight = np.clip((1.55 - zs) / 0.07, 0.0, 1.0)
        xs *= (1.0 + 0.20 * neck_weight)
        ys *= (1.0 + 0.18 * neck_weight)
        
        # Restore eyes/mouth
        xs[protected] = orig[:, 0][protected]
        ys[protected] = orig[:, 1][protected]
        zs[protected] = orig[:, 2][protected]
        
        for i, v in enumerate(head.data.vertices):
            v.co.x = xs[i]
            v.co.y = ys[i]
            v.co.z = zs[i]
        head.data.update()
        print('Morphed Balen Head: Bigger, broader skull with deep occiput & massive neck!')
        
    # 2. Morph Body & OutfitTop (Broad muscular chest, wide shoulders)
    for obj_name in ['OutfitTop', 'Body']:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            coords = np.array([v.co for v in obj.data.vertices])
            xs = coords[:, 0]
            ys = coords[:, 1]
            zs = coords[:, 2]
            
            # Collar / Neck matching (Z in [1.44, 1.56])
            neck_w = np.clip((zs - 1.42) / 0.06, 0.0, 1.0) * np.clip((1.58 - zs) / 0.06, 0.0, 1.0)
            xs *= (1.0 + 0.18 * neck_w)
            ys *= (1.0 + 0.16 * neck_w)
            
            # Broad shoulders & chest (Z in [1.15, 1.52])
            chest_w = np.clip((zs - 1.10) / 0.15, 0.0, 1.0) * np.clip((1.54 - zs) / 0.10, 0.0, 1.0)
            xs *= (1.0 + 0.15 * chest_w) # 15% wider shoulders
            ys *= (1.0 + 0.12 * chest_w) # 12% deeper chest/back
            
            # Upper arms thickness (|X| in [0.20, 0.55], Z in [1.10, 1.45])
            arm_w = (np.abs(xs) > 0.20) & (zs > 1.05) & (zs < 1.45)
            ys *= (1.0 + 0.10 * arm_w)
            
            for i, v in enumerate(obj.data.vertices):
                v.co.x = xs[i]
                v.co.y = ys[i]
                v.co.z = zs[i]
            obj.data.update()
            print(f'Morphed {obj_name}: Broader shoulders, thick muscular chest!')
            
    # 3. Overall taller scale for Balen (Tall alpha politician)
    armature = bpy.data.objects.get('Armature')
    if armature:
        armature.scale = (1.05, 1.05, 1.06)
        print('Scaled Armature to 1.06x height for Balen!')
