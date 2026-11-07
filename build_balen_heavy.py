import bpy, os, sys, shutil

sys.path.append('.')
import morph_balen_heavy

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='public/models/rahul.glb')

# 1. Apply Heavy Body & Bigger Skull Morph
morph_balen_heavy.morph_balen_heavy()

# 2. Assign Head Texture
head_img = bpy.data.images.load(os.path.abspath('balen_v2_aligned_gltf.png'))
mat_head = bpy.data.materials.get('AvatarHead')
if mat_head and mat_head.node_tree:
    for n in mat_head.node_tree.nodes:
        if n.type == 'TEX_IMAGE':
            n.image = head_img

# 3. Black outfit
for mname in ['outfit_top', 'outfit_bottom']:
    mat = bpy.data.materials.get(mname)
    if mat and mat.node_tree:
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.025, 1.0)
            for n in list(mat.node_tree.nodes):
                if n.type == 'TEX_IMAGE':
                    mat.node_tree.nodes.remove(n)

# 4. Export to public/models/balen.glb, public/models/mobile/balen.glb, and yogi.glb
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
print('Exported big heavy Balen to public models!')
