import bpy
import numpy as np
import os
import shutil

def fit_skull_to_user_360():
    print("=== FITTING BLENDER SKULL & UVS TO USER 360 FACE ===")
    
    # 1. User texture for glTF
    gltf_user_path = os.path.abspath('user_360_balen_gltf.png')
    
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath='public/models/rahul.glb')
    
    head = bpy.data.objects.get('Head')
    mesh = head.data
    uv_layer = mesh.uv_layers.active.data
    
    # 2. Adjust UV mapping of Head mesh so vertices land EXACTLY on user's 360 features:
    # In upright space:
    # Original eyes: Y = 335 -> User eyes: Y = 441
    # Original mouth: Y = 525 -> User mouth: Y = 598
    # Original chin: Y = 650 -> User chin: Y = 770
    # Original topi: Y = 240 -> User topi rim: Y = 320
    # Original crown: Y = 10 -> User crown: Y = 50
    # In glTF UV space (V = 1.0 - Y/1024):
    # Orig V: [0.99, 0.765, 0.673, 0.487, 0.365, 0.15]
    # User V: [0.95, 0.687, 0.569, 0.416, 0.248, 0.05]
    
    orig_v_keys = np.array([0.00, 0.15, 0.365, 0.487, 0.673, 0.765, 0.99, 1.00])
    user_v_keys = np.array([0.00, 0.05, 0.248, 0.416, 0.569, 0.687, 0.95, 1.00])
    
    for loop in uv_layer:
        u, v = loop.uv
        # Interpolate V smoothly to match user's landmark positions
        new_v = np.interp(v, orig_v_keys, user_v_keys)
        loop.uv = (u, float(new_v))
        
    print("Adjusted Head UV coordinates to fit user 360 face landmarks!")
    
    # 3. Morph 3D Skull Geometry to match Balen's big powerful build
    coords = np.array([v.co for v in mesh.vertices])
    xs = coords[:, 0]
    ys = coords[:, 1]
    zs = coords[:, 2]
    orig_co = coords.copy()
    
    # A. Deeper, fuller back of skull (occiput)
    back_mask = np.clip((ys - 0.01) / 0.05, 0.0, 1.0) * np.clip((zs - 1.50) / 0.10, 0.0, 1.0)
    ys += 0.025 * back_mask
    
    # B. Taller cranium for Bhadgaunle Topi height
    cranium_mask = np.clip((zs - 1.68) / 0.12, 0.0, 1.0)
    zs += 0.020 * cranium_mask
    xs *= (1.0 + 0.10 * cranium_mask)
    
    # C. Broad masculine square jaw (mandibular angles)
    jaw_weight = np.clip((zs - 1.52) / 0.04, 0.0, 1.0) * np.clip((1.64 - zs) / 0.05, 0.0, 1.0)
    jaw_lat = jaw_weight * np.clip((np.abs(xs) - 0.025) / 0.04, 0.0, 1.0)
    xs *= (1.0 + 0.16 * jaw_lat)
    
    # D. Strong chin
    chin_mask = np.clip((zs - 1.52) / 0.03, 0.0, 1.0) * np.clip((1.59 - zs) / 0.03, 0.0, 1.0) * (ys < -0.065)
    ys -= 0.010 * chin_mask
    xs *= (1.0 + 0.08 * chin_mask)
    
    # E. Massive thick neck
    neck_weight = np.clip((1.55 - zs) / 0.07, 0.0, 1.0)
    xs *= (1.0 + 0.22 * neck_weight)
    ys *= (1.0 + 0.20 * neck_weight)
    
    # Eye and mouth protection
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
    print("Morphed 3D skull geometry!")
    
    # 4. Morph Body & OutfitTop (Broad muscular chest & shoulders)
    for obj_name in ['OutfitTop', 'Body']:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            coords = np.array([v.co for v in obj.data.vertices])
            xs = coords[:, 0]
            ys = coords[:, 1]
            zs = coords[:, 2]
            
            # Collar / neck widening
            neck_w = np.clip((zs - 1.42) / 0.06, 0.0, 1.0) * np.clip((1.58 - zs) / 0.06, 0.0, 1.0)
            xs *= (1.0 + 0.20 * neck_w)
            ys *= (1.0 + 0.18 * neck_w)
            
            # Broad shoulders & deep chest
            chest_w = np.clip((zs - 1.10) / 0.15, 0.0, 1.0) * np.clip((1.54 - zs) / 0.10, 0.0, 1.0)
            xs *= (1.0 + 0.16 * chest_w)
            ys *= (1.0 + 0.14 * chest_w)
            
            for i, v in enumerate(obj.data.vertices):
                v.co.x = xs[i]
                v.co.y = ys[i]
                v.co.z = zs[i]
            obj.data.update()
            
    # 5. Assign user's exact 360 texture to AvatarHead
    head_img = bpy.data.images.load(gltf_user_path)
    mat_head = bpy.data.materials.get('AvatarHead')
    if mat_head and mat_head.node_tree:
        for n in mat_head.node_tree.nodes:
            if n.type == 'TEX_IMAGE':
                n.image = head_img
                print("Assigned user 360 texture directly to AvatarHead!")
                
    # 6. Outfit colors
    for mname in ['outfit_top', 'outfit_bottom']:
        mat = bpy.data.materials.get(mname)
        if mat and mat.node_tree:
            bsdf = mat.node_tree.nodes.get('Principled BSDF')
            if bsdf:
                bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.025, 1.0)
                for n in list(mat.node_tree.nodes):
                    if n.type == 'TEX_IMAGE':
                        mat.node_tree.nodes.remove(n)

    # 7. Export GLBs and save .blend file
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
    
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('balen_user_exact.blend'))
    print("Exported balen.glb and saved balen_user_exact.blend!")

if __name__ == '__main__':
    fit_skull_to_user_360()
