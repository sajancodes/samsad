import struct, os, json

def extract_images(glb_path, out_prefix):
    with open(glb_path, 'rb') as f:
        data = f.read()
    magic, ver, length = struct.unpack_from('<4sII', data, 0)
    json_len, json_type = struct.unpack_from('<II', data, 12)
    gltf = json.loads(data[20:20+json_len].decode('utf-8'))
    bin_offset = 20 + json_len
    bin_len, bin_type = struct.unpack_from('<II', data, bin_offset)
    bin_bytes = data[bin_offset+8 : bin_offset+8+bin_len]
    
    for i, img in enumerate(gltf.get('images', [])):
        bv = gltf['bufferViews'][img['bufferView']]
        offset = bv.get('byteOffset', 0)
        blen = bv['byteLength']
        img_data = bin_bytes[offset:offset+blen]
        mime = img.get('mimeType', 'image/png')
        ext = 'jpg' if 'jpeg' in mime else 'png'
        img_name = img.get('name', f'img_{i}')
        out_name = f'{out_prefix}_{img_name}.{ext}'
        with open(out_name, 'wb') as out_f:
            out_f.write(img_data)
        print(f'Extracted {out_name} ({len(img_data)} bytes)')

for name in ['modi', 'trump', 'yogi', 'nitin', 'ravi']:
    extract_images(f'public/models/{name}.glb', f'orig_{name}')
