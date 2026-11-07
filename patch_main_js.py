with open('public/assets/main-samsad3d.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace Ac mapping
old_ac = 'Ac={modi:`${Dc}modi.glb${kc}`,rahul:`${Dc}rahul.glb${kc}`,didi:`${Dc}didi.glb${kc}`,trump:`${Dc}trump.glb${kc}`,yogi:`${Dc}yogi.glb${kc}`,nitin:`${Dc}nitin.glb${kc}`,mbapu:`${Dc}mbapu.glb${Oc}`,ravi:`${Dc}ravi.glb${kc}`,lalu:`${Dc}lalu.glb${kc}`}'
new_ac = 'Ac={modi:`${Dc}kpoli.glb${kc}`,rahul:`${Dc}gagan.glb${kc}`,didi:`${Dc}harka.glb${kc}`,trump:`${Dc}durga.glb${kc}`,yogi:`${Dc}balen.glb${kc}`,nitin:`${Dc}deuba.glb${kc}`,mbapu:`${Dc}genz.glb${Oc}`,ravi:`${Dc}rabi.glb${kc}`,lalu:`${Dc}prachanda.glb${kc}`}'

# Replace jc mapping
old_jc = 'jc={modi:`/models/modi.glb${kc}`,rahul:`/models/rahul.glb${kc}`,didi:`/models/didi.glb${kc}`,trump:`/models/trump.glb${kc}`,yogi:`/models/yogi.glb${kc}`,nitin:`/models/nitin.glb${kc}`,mbapu:`/models/mbapu.glb${Oc}`,ravi:`/models/ravi.glb${kc}`,lalu:`/models/lalu.glb${kc}`}'
new_jc = 'jc={modi:`/models/kpoli.glb${kc}`,rahul:`/models/gagan.glb${kc}`,didi:`/models/harka.glb${kc}`,trump:`/models/durga.glb${kc}`,yogi:`/models/balen.glb${kc}`,nitin:`/models/deuba.glb${kc}`,mbapu:`/models/genz.glb${Oc}`,ravi:`/models/rabi.glb${kc}`,lalu:`/models/prachanda.glb${kc}`}'

if old_ac in text and old_jc in text:
    text = text.replace(old_ac, new_ac)
    text = text.replace(old_jc, new_jc)
    with open('public/assets/main-samsad3d.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Successfully patched main-samsad3d.js with direct Nepali model paths!')
else:
    print('Target strings not found! Searching...')
    import re
    print('Ac found:', 'Ac={' in text)
    print('jc found:', 'jc={' in text)
