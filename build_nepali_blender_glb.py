import bpy
import os
import shutil
import sys

LEGACY_MAP = {
    'kpoli': 'modi',
    'balen': 'yogi',
    'harka': 'didi',
    'durga': 'trump',
    'gagan': 'rahul',
    'deuba': 'nitin',
    'prachanda': 'lalu',
    'rabi': 'ravi',
    'genz': 'mbapu'
}

def build_character_glb(
    char_id,
    head_tex_path,
    outfit_top_color=(0.15, 0.16, 0.18, 1.0),
    outfit_bottom_color=(0.10, 0.10, 0.12, 1.0),
    shoes_color=(0.04, 0.04, 0.04, 1.0),
    eyelash_color=(0.12, 0.10, 0.09, 1.0)
):
    print(f'=== BLENDER: BUILDING RIGGED 3D GLB FOR {char_id.upper()} ===')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # 1. Import base rigged humanoid (74-bone skeleton)
    bpy.ops.import_scene.gltf(filepath='public/models/rahul.glb')
    
    # 2. Assign 360° Complete Head Texture
    head_img = bpy.data.images.load(os.path.abspath(head_tex_path))
    mat_head = bpy.data.materials.get('AvatarHead')
    if mat_head and mat_head.node_tree:
        for n in mat_head.node_tree.nodes:
            if n.type == 'TEX_IMAGE':
                n.image = head_img
                print(f'Assigned 360° head texture to AvatarHead!')
                
    # 3. Soften eyelashes
    mat_el = bpy.data.materials.get('AvatarEyelashes')
    if mat_el and mat_el.node_tree:
        bsdf = mat_el.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = eyelash_color
            bsdf.inputs['Roughness'].default_value = 0.9
            
    # 4. Style Outfit (Authentic Nepali Clothes)
    # Coat / Daura Top
    mat_top = bpy.data.materials.get('outfit_top')
    if mat_top and mat_top.node_tree:
        bsdf = mat_top.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = outfit_top_color
            bsdf.inputs['Roughness'].default_value = 0.8
            for n in list(mat_top.node_tree.nodes):
                if n.type == 'TEX_IMAGE':
                    mat_top.node_tree.nodes.remove(n)

    # Suruwal / Trousers
    mat_bot = bpy.data.materials.get('outfit_bottom')
    if mat_bot and mat_bot.node_tree:
        bsdf = mat_bot.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = outfit_bottom_color
            bsdf.inputs['Roughness'].default_value = 0.85
            for n in list(mat_bot.node_tree.nodes):
                if n.type == 'TEX_IMAGE':
                    mat_bot.node_tree.nodes.remove(n)

    # Shoes
    mat_shoes = bpy.data.materials.get('outfit_shoes')
    if mat_shoes and mat_shoes.node_tree:
        bsdf = mat_shoes.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = shoes_color
            bsdf.inputs['Roughness'].default_value = 0.35
            for n in list(mat_shoes.node_tree.nodes):
                if n.type == 'TEX_IMAGE':
                    mat_shoes.node_tree.nodes.remove(n)

    # 5. Export to desktop and mobile paths
    os.makedirs('public/models', exist_ok=True)
    os.makedirs('public/models/mobile', exist_ok=True)
    
    out_desktop = os.path.abspath(f'public/models/{char_id}.glb')
    out_mobile = os.path.abspath(f'public/models/mobile/{char_id}.glb')
    
    bpy.ops.export_scene.gltf(
        filepath=out_desktop,
        export_format='GLB',
        use_selection=False,
        export_apply=False,
        export_draco_mesh_compression_enable=True
    )
    shutil.copyfile(out_desktop, out_mobile)
    
    # Also overwrite the legacy slot in both desktop & mobile so no old assets remain
    legacy = LEGACY_MAP.get(char_id)
    if legacy:
        shutil.copyfile(out_desktop, f'public/models/{legacy}.glb')
        shutil.copyfile(out_desktop, f'public/models/mobile/{legacy}.glb')
        print(f'Overwrote legacy slot: {legacy}.glb')
        
    print(f'Successfully exported {char_id} to {out_desktop} and {out_mobile}!')

if __name__ == '__main__':
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    cid = args[0] if len(args) > 0 else 'kpoli'
    tex = args[1] if len(args) > 1 else f'{cid}_head_tex.png'
    
    top_r = float(args[2]) if len(args) > 2 else 0.15
    top_g = float(args[3]) if len(args) > 3 else 0.16
    top_b = float(args[4]) if len(args) > 4 else 0.18
    
    bot_r = float(args[5]) if len(args) > 5 else 0.10
    bot_g = float(args[6]) if len(args) > 6 else 0.10
    bot_b = float(args[7]) if len(args) > 7 else 0.12
    
    build_character_glb(
        char_id=cid,
        head_tex_path=tex,
        outfit_top_color=(top_r, top_g, top_b, 1.0),
        outfit_bottom_color=(bot_r, bot_g, bot_b, 1.0)
    )
