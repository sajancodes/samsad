import struct, json, os
from PIL import Image

path = 'public/models/rahul.glb'
with open(path, 'rb') as f:
    data = f.read()

magic, ver, length = struct.unpack('<4sII', data[:12])
chunk_len, chunk_type = struct.unpack('<II', data[12:20])
gltf = json.loads(data[20:20+chunk_len].decode('utf-8'))
bin_offset = 20 + chunk_len
bin_len, bin_type = struct.unpack('<II', data[bin_offset:bin_offset+8])
bin_data = data[bin_offset+8:bin_offset+8+bin_len]

for mat in gltf.get('materials', []):
    mname = mat.get('name', '')
    if 'head' in mname.lower():
        pbr = mat.get('pbrMetallicRoughness', {})
        bc = pbr.get('baseColorTexture', {})
        t_idx = bc.get('index')
        if t_idx is not None:
            tex = gltf['textures'][t_idx]
            img_idx = tex.get('source')
            if img_idx is None and 'extensions' in tex:
                img_idx = tex['extensions'].get('EXT_texture_webp', {}).get('source')
            if img_idx is not None:
                img = gltf['images'][img_idx]
                bv = gltf['bufferViews'][img['bufferView']]
                off = bv.get('byteOffset', 0)
                blen = bv['byteLength']
                raw_tex_path = 'base_head_raw.webp'
                with open(raw_tex_path, 'wb') as fo:
                    fo.write(bin_data[off:off+blen])
                
                im = Image.open(raw_tex_path).convert('RGB')
                im.save('base_head_raw.png')
                # Flip upright for compositing
                upright = im.transpose(Image.FLIP_TOP_BOTTOM)
                upright.save('base_head_upright.png')
                print(f'Successfully extracted base head! Size: {im.size}')
