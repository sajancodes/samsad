import bpy
import numpy as np
import os
import shutil

def sculpt_authentic_balen_skull():
    print("=== SCULPTING AUTHENTIC BALEN SHAH SKULL IN BLENDER ===")
    
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath='public/models/rahul.glb')
    
    head = bpy.data.objects.get('Head')
    mesh = head.data
    coords = np.array([v.co for v in mesh.vertices])
    
    xs = coords[:, 0]
    ys = coords[:, 1]
    zs = coords[:, 2]
    orig_co = coords.copy()
    
    # 1. AUTHENTIC TALL BHADGAUNLE TOPI CROWN:
    # Look at real Balen: his topi stands ~6cm above his brow!
    # Pull the cranium top (Z > 1.70) UPWARDS by +0.055m in a smooth cylindrical form:
    cranium_top = np.clip((zs - 1.70) / 0.10, 0.0, 1.0)
    zs += 0.055 * (cranium_top ** 1.5)
    # Give the topi a slight cylindrical flare:
    xs *= (1.0 + 0.08 * cranium_top)
    
    # 2. FULL, ROUNDED BALEN CHEEKS (Asian / Nepali facial structure):
    # Expand mid-cheeks laterally and forward:
    cheek_mask = np.clip((zs - 1.57) / 0.05, 0.0, 1.0) * np.clip((1.68 - zs) / 0.05, 0.0, 1.0) * (np.abs(xs) > 0.025)
    xs *= (1.0 + 0.12 * cheek_mask)
    ys -= 0.008 * cheek_mask * (ys < -0.04) # push cheeks forward, eliminate sunken look!
    
    # 3. ROUNDED, FIRM CHIN (NOT SHARP, NOT POINTED):
    chin_zone = (zs > 1.52) & (zs < 1.58) & (ys < -0.07)
    # Pull chin slightly upward and round it:
    zs[chin_zone] += 0.005
    xs[chin_zone] *= 1.10 # wider, rounder chin
    
    # 4. BROADEN JAWLINE (Firm mandibular width):
    jaw_zone = (zs > 1.52) & (zs < 1.63) & (np.abs(xs) > 0.035) & (ys > -0.06)
    xs[jaw_zone] *= 1.14
    
    # 5. ROUNDED OCCIPUT (Back of skull):
    back_mask = np.clip((ys - 0.0) / 0.06, 0.0, 1.0) * np.clip((zs - 1.50) / 0.12, 0.0, 1.0)
    ys += 0.022 * back_mask
    
    # 6. THICK, STRONG NECK:
    neck_mask = np.clip((1.55 - zs) / 0.07, 0.0, 1.0)
    xs *= (1.0 + 0.20 * neck_mask)
    ys *= (1.0 + 0.18 * neck_mask)
    
    # Protect inner mouth & eye openings:
    is_eye = (np.abs(xs) < 0.055) & (zs > 1.65) & (zs < 1.71) & (ys < -0.07)
    is_mouth = (np.abs(xs) < 0.032) & (zs > 1.58) & (zs < 1.64) & (ys < -0.10)
    prot = is_eye | is_mouth
    xs[prot] = orig_co[:, 0][prot]
    ys[prot] = orig_co[:, 1][prot]
    zs[prot] = orig_co[:, 2][prot]
    
    for i, v in enumerate(mesh.vertices):
        v.co.x = xs[i]
        v.co.y = ys[i]
        v.co.z = zs[i]
    mesh.update()
    print("Sculpted authentic Balen skull geometry!")
    
    # Morph Body and OutfitTop for broad shoulders
    for obj_name in ['OutfitTop', 'Body']:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            coords = np.array([v.co for v in obj.data.vertices])
            xs = coords[:, 0]
            ys = coords[:, 1]
            zs = coords[:, 2]
            
            neck_w = np.clip((zs - 1.40) / 0.08, 0.0, 1.0) * np.clip((1.56 - zs) / 0.08, 0.0, 1.0)
            xs *= (1.0 + 0.20 * neck_w)
            ys *= (1.0 + 0.18 * neck_w)
            
            chest_w = np.clip((zs - 1.10) / 0.15, 0.0, 1.0) * np.clip((1.54 - zs) / 0.10, 0.0, 1.0)
            xs *= (1.0 + 0.16 * chest_w)
            ys *= (1.0 + 0.14 * chest_w)
            
            for i, v in enumerate(obj.data.vertices):
                v.co.x = xs[i]
                v.co.y = ys[i]
                v.co.z = zs[i]
            obj.data.update()
            
    # Assign calibrated texture
    head_img = bpy.data.images.load(os.path.abspath('balen_v2_aligned_gltf.png'))
    mat_head = bpy.data.materials.get('AvatarHead')
    if mat_head and mat_head.node_tree:
        for n in mat_head.node_tree.nodes:
            if n.type == 'TEX_IMAGE':
                n.image = head_img

    # Dark suit
    for mname in ['outfit_top', 'outfit_bottom']:
        mat = bpy.data.materials.get(mname)
        if mat and mat.node_tree:
            bsdf = mat.node_tree.nodes.get('Principled BSDF')
            if bsdf:
                bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.025, 1.0)
                for n in list(mat.node_tree.nodes):
                    if n.type == 'TEX_IMAGE':
                        mat.node_tree.nodes.remove(n)

    out_desktop = os.path.abspath('public/models/balen.glb')
    out_mobile = os.path.abspath('public/models/mobile/balen.glb')
    out_legacy = os.path.abspath('public/models/yogi.glb')
    
    bpy.ops.export_scene.gltf(
        filepath=out_desktop,
        export_format='GLB',
        export_draco_mesh_compression_enable=True
    )
    shutil.copyfile(out_desktop, out_mobile)
    shutil.copyfile(out_desktop, out_legacy)
    shutil.copyfile(out_desktop, os.path.abspath('public/models/mobile/yogi.glb'))
    
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('balen_authentic.blend'))
    print("Exported authentic balen.glb and saved balen_authentic.blend!")

if __name__ == '__main__':
    sculpt_authentic_balen_skull()
