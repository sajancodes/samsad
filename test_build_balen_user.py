import bpy
import os
import sys

sys.path.append('.')
import morph_head

# 1. Blender build
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='public/models/rahul.glb')

# Apply Balen square jaw / tall cranium morph
head = bpy.data.objects.get('Head')
morph_head.apply_skull_morph(head, 'balen')

# Assign texture
head_img = bpy.data.images.load(os.path.abspath('balen_unwrap_gltf.png'))
mat_head = bpy.data.materials.get('AvatarHead')
if mat_head and mat_head.node_tree:
    for n in mat_head.node_tree.nodes:
        if n.type == 'TEX_IMAGE':
            n.image = head_img

# Black suit
for mname in ['outfit_top', 'outfit_bottom']:
    mat = bpy.data.materials.get(mname)
    if mat and mat.node_tree:
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.025, 1.0)
            for n in list(mat.node_tree.nodes):
                if n.type == 'TEX_IMAGE':
                    mat.node_tree.nodes.remove(n)

bpy.ops.export_scene.gltf(filepath='test_balen_user_unwrap.glb', export_format='GLB')
print('Exported test_balen_user_unwrap.glb')
