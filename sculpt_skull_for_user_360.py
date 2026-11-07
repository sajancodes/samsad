import bpy
import numpy as np
import os
import shutil

def sculpt_skull_for_user_360():
    print("=== SCULPTING 3D SKULL & EYE SOCKETS TO FIT USER 360 FACE ===")
    
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath='public/models/rahul.glb')
    
    gltf_user_path = os.path.abspath('user_360_balen_gltf.png')
    
    # In user 360 texture:
    # Eyes are lower by about 0.045m in 3D space
    # Forehead / Topi is taller by about 0.040m
    
    # 1. Shift Eye and Eyelash sub-meshes down to match sunglasses
    for ename in ['EyeL', 'EyeR', 'EyeCorneaL', 'EyeCorneaR', 'Eyelashes']:
        obj = bpy.data.objects.get(ename)
        if obj:
            for v in obj.data.vertices:
                v.co.z -= 0.042
                v.co.y += 0.005 # slightly forward
            obj.data.update()
            print(f'Shifted {ename} down to sunglasses level!')
            
    # 2. Morph Head mesh to match user 360 skull proportions:
    head = bpy.data.objects.get('Head')
    if head:
        coords = np.array([v.co for v in head.data.vertices])
        xs = coords[:, 0]
        ys = coords[:, 1]
        zs = coords[:, 2]
        
        # Lower the 3D eye socket hollows and nose bridge:
        eye_zone = (zs > 1.63) & (zs < 1.73) & (np.abs(xs) < 0.065) & (ys < -0.04)
        zs[eye_zone] -= 0.040
        
        # Lower the 3D nose tip:
        nose_zone = (zs > 1.61) & (zs < 1.68) & (np.abs(xs) < 0.035) & (ys < -0.09)
        zs[nose_zone] -= 0.035
        
        # Lower mouth and jaw slightly
        mouth_jaw = (zs > 1.50) & (zs < 1.63) & (ys < -0.04)
        zs[mouth_jaw] -= 0.020
        
        # Deepen back of head (occiput) for big skull:
        back_mask = np.clip((ys - 0.01) / 0.05, 0.0, 1.0) * np.clip((zs - 1.50) / 0.10, 0.0, 1.0)
        ys += 0.030 * back_mask
        
        # Broaden square jaw corners:
        jaw_corners = (zs > 1.48) & (zs < 1.62) & (np.abs(xs) > 0.03) & (ys > -0.06) & (ys < 0.03)
        xs[jaw_corners] *= 1.18
        
        # Thicken neck:
        neck_mask = np.clip((1.54 - zs) / 0.07, 0.0, 1.0)
        xs *= (1.0 + 0.22 * neck_mask)
        ys *= (1.0 + 0.20 * neck_mask)
        
        # Make tall cranium dome:
        cranium_mask = np.clip((zs - 1.66) / 0.14, 0.0, 1.0)
        zs += 0.028 * cranium_mask
        xs *= (1.0 + 0.12 * cranium_mask)
        
        for i, v in enumerate(head.data.vertices):
            v.co.x = xs[i]
            v.co.y = ys[i]
            v.co.z = zs[i]
        head.data.update()
        print('Morphed Head 3D geometry to fit user 360 proportions!')
        
    # 3. Morph Body and OutfitTop (broad athletic frame)
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
            
    # 4. Map user 360 texture directly to AvatarHead
    head_img = bpy.data.images.load(gltf_user_path)
    mat_head = bpy.data.materials.get('AvatarHead')
    if mat_head and mat_head.node_tree:
        for n in mat_head.node_tree.nodes:
            if n.type == 'TEX_IMAGE':
                n.image = head_img

    # 5. Black suit
    for mname in ['outfit_top', 'outfit_bottom']:
        mat = bpy.data.materials.get(mname)
        if mat and mat.node_tree:
            bsdf = mat.node_tree.nodes.get('Principled BSDF')
            if bsdf:
                bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.025, 1.0)
                for n in list(mat.node_tree.nodes):
                    if n.type == 'TEX_IMAGE':
                        mat.node_tree.nodes.remove(n)

    # 6. Export GLB
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
    
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('balen_user_fitted.blend'))
    print("Exported custom sculpted balen.glb and saved balen_user_fitted.blend!")

if __name__ == '__main__':
    sculpt_skull_for_user_360()
