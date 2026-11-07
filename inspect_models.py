import re

with open('public/assets/main-samsad3d.js', 'r', encoding='utf-8') as f:
    text = f.read()

for m in re.finditer(r'([a-zA-Z0-9_\-\/]+\.glb)', text):
    start = max(0, m.start() - 80)
    end = min(len(text), m.end() + 80)
    print('Match:', m.group(0))
    print('Snippet:', text[start:end])
    print('-'*50)
