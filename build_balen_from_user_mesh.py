import bpy
import bmesh
import numpy as np
import os
import shutil
import math

def build_final_balen():
    print("=== BUILDING FINAL BALEN WITH PROPER ARMATURE RIGGING ===")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # 1. Import base avatar with combat animations & skeleton
    bpy.ops.import_scene.gltf(filepath='public/models/rahul.glb')
    arm = bpy.data.objects.get('Rig')
    if not arm:
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE':
                arm = obj
                break
    print(f'Found Armature: {arm.name}')
    
    # 2. Import user 3D head model
    user_glb = r'C:/Users/ab429/.gemini/antigravity/brain/f3dd405d-d87b-4bab-aed2-1613e1574d1e/.user_uploaded/media_1794036478740_eb168a9c.glb'
    bpy.ops.import_scene.gltf(filepath=user_glb)
    
    user_head = None
    for obj in bpy.data.objects:
        if 'tripo' in obj.name:
            user_head = obj
            break
            
    user_head.name = 'BalenHead'
    
    # 3. Cleanly trim bottom base (Z < 0.04) and taper lower neck so it sits inside collar
    bm = bmesh.new()
    bm.from_mesh(user_head.data)
    verts_to_delete = [v for v in bm.verts if v.co.z < 0.04]
    bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')
    
    # Smooth taper on bottom 10cm of neck
    for v in bm.verts:
        if v.co.z < 0.14:
            factor = (v.co.z - 0.04) / 0.10
            t = 0.72 + 0.28 * factor
            v.co.x *= t
            v.co.y *= t
            
    bm.to_mesh(user_head.data)
    bm.free()
    user_head.data.update()
    
    # 4. Decimate to optimize polygon count for 60fps web gameplay
    dec = user_head.modifiers.new(name='Decimate', type='DECIMATE')
    dec.ratio = 0.40
    bpy.context.view_layer.objects.active = user_head
    bpy.ops.object.modifier_apply(modifier='Decimate')
    print(f'Optimized head mesh: {len(user_head.data.vertices)} vertices')
    
    # 5. Position & Scale user head
    scale = 0.38
    user_head.scale = (scale, scale, scale)
    user_head.location = (0.0, -0.02, 1.45)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # 6. Rig to Armature with EXACT bone names: Head_08 and Neck2_07
    vg_head8 = user_head.vertex_groups.new(name='Head_08')
    vg_neck2 = user_head.vertex_groups.new(name='Neck2_07')
    vg_head = user_head.vertex_groups.new(name='Head')
    vg_neck = user_head.vertex_groups.new(name='Neck')
    
    coords = np.array([v.co for v in user_head.data.vertices])
    zs = coords[:, 2]
    
    for i, z in enumerate(zs):
        if z > 1.56:
            vg_head8.add([i], 1.0, 'REPLACE')
            vg_head.add([i], 1.0, 'REPLACE')
        elif z < 1.51:
            vg_neck2.add([i], 1.0, 'REPLACE')
            vg_neck.add([i], 1.0, 'REPLACE')
        else:
            t = (z - 1.51) / 0.05
            vg_head8.add([i], float(t), 'REPLACE')
            vg_head.add([i], float(t), 'REPLACE')
            vg_neck2.add([i], float(1.0 - t), 'REPLACE')
            vg_neck.add([i], float(1.0 - t), 'REPLACE')
            
    arm_mod = user_head.modifiers.new(name='Armature', type='ARMATURE')
    arm_mod.object = arm
    user_head.parent = arm
    print('Parented BalenHead to Rig with Head_08 & Neck2_07 weights!')
    
    # 7. Remove original Ready Player Me head and facial elements
    for name in ['Head', 'EyeCorneaL', 'EyeCorneaR', 'EyeL', 'EyeR', 'Eyelashes', 'TeethLower', 'TeethUpper']:
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)
            
    # Remove any stray objects like Icosphere
    for obj in list(bpy.data.objects):
        if 'Icosphere' in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)
            
    # 8. Broaden OutfitTop collar & shoulders for authentic mayor physique
    outfit = bpy.data.objects.get('OutfitTop')
    if outfit:
        mesh = outfit.data
        coords = np.array([v.co for v in mesh.vertices])
        xs = coords[:, 0]
        ys = coords[:, 1]
        zs = coords[:, 2]
        
        shoulder_w = np.clip((zs - 1.15) / 0.15, 0.0, 1.0) * np.clip((1.55 - zs) / 0.10, 0.0, 1.0)
        xs *= (1.0 + 0.12 * shoulder_w)
        ys *= (1.0 + 0.10 * shoulder_w)
        
        collar_mask = zs > 1.47
        zs[collar_mask] += 0.015
        
        for i, v in enumerate(mesh.vertices):
            v.co.x = xs[i]
            v.co.y = ys[i]
            v.co.z = zs[i]
        mesh.update()
        
    # 9. Outfit Colors (Pure Black / Charcoal Daura Suruwal)
    for mname in ['outfit_top', 'outfit_bottom']:
        mat = bpy.data.materials.get(mname)
        if mat and mat.node_tree:
            bsdf = mat.node_tree.nodes.get('Principled BSDF')
            if bsdf:
                bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.025, 1.0)
                bsdf.inputs['Roughness'].default_value = 0.85
                for n in list(mat.node_tree.nodes):
                    if n.type == 'TEX_IMAGE':
                        mat.node_tree.nodes.remove(n)

    # 10. Multi-Angle Studio Previews
    cam_data = bpy.data.cameras.new('RenderCam')
    cam = bpy.data.objects.new('RenderCam', cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    
    # Lighting
    for loc, energy, rot in [
        ((0.0, -2.5, 2.0), 3.8, (math.radians(45), math.radians(15), 0)),
        ((-2.0, -1.5, 1.8), 2.4, (math.radians(35), math.radians(-30), math.radians(-40))),
        ((2.0, 1.5, 2.2), 3.0, (math.radians(-50), 0, math.radians(140)))
    ]:
        ld = bpy.data.lights.new('StudioLight', type='SUN')
        ld.energy = energy
        lo = bpy.data.objects.new('StudioLight', ld)
        lo.location = loc
        lo.rotation_euler = rot
        bpy.context.scene.collection.objects.link(lo)
        
    bpy.context.scene.render.resolution_x = 768
    bpy.context.scene.render.resolution_y = 768
    
    # Render Front Portrait
    cam.location = (0, -0.85, 1.62)
    cam.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.scene.render.filepath = os.path.abspath('balen_final_portrait.png')
    bpy.ops.render.render(write_still=True)
    print('Rendered balen_final_portrait.png')

    # Render 3/4 Action View
    cam.location = (-0.75, -1.1, 1.58)
    cam.rotation_euler = (math.radians(82), 0, math.radians(-35))
    bpy.context.scene.render.filepath = os.path.abspath('balen_final_34.png')
    bpy.ops.render.render(write_still=True)
    print('Rendered balen_final_34.png')

    # 11. Export GLBs with Draco compression
    out_desktop = os.path.abspath('public/models/balen.glb')
    out_mobile = os.path.abspath('public/models/mobile/balen.glb')
    out_yogi = os.path.abspath('public/models/yogi.glb')
    out_mobile_yogi = os.path.abspath('public/models/mobile/yogi.glb')
    
    bpy.ops.export_scene.gltf(
        filepath=out_desktop,
        export_format='GLB',
        export_draco_mesh_compression_enable=True
    )
    print(f'Exported {out_desktop} (Size: {os.path.getsize(out_desktop)} bytes)')
    
    shutil.copyfile(out_desktop, out_mobile)
    shutil.copyfile(out_desktop, out_yogi)
    shutil.copyfile(out_desktop, out_mobile_yogi)
    
    # Save Blender project
    blend_path = os.path.abspath('blender_models/balen.blend')
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    shutil.copyfile(blend_path, os.path.abspath('balen_authentic.blend'))
    print('Saved blender_models/balen.blend and balen_authentic.blend!')

if __name__ == '__main__':
    build_final_balen()
