import urllib.request
import os
from PIL import Image

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

URLS = {
    'balen': 'https://upload.wikimedia.org/wikipedia/commons/4/44/Prime_Minister_of_Nepal_Official_Portrait_Photo_Balen.jpg',
    'kpoli': 'https://upload.wikimedia.org/wikipedia/commons/d/dd/The_Prime_Minister_of_Nepal%2C_Shri_KP_Sharma_Oli_at_Bangkok%2C_in_Thailand_on_April_04%2C_2025_%28cropped%29.jpg',
    'deuba': 'https://upload.wikimedia.org/wikipedia/commons/f/fe/Sher_Bahadur_Deuba_November_2021_crop.jpg',
    'prachanda': 'https://upload.wikimedia.org/wikipedia/commons/8/88/Prime_Minister_of_Nepal_Pushpa_Kamal_Dahal_%22Prachanda%22.jpg',
    'rabi': 'https://upload.wikimedia.org/wikipedia/commons/c/ce/Rabi_Lamichhane.png',
    'harka': 'https://upload.wikimedia.org/wikipedia/commons/7/76/Harka_Sampang_%28cropped%29.png',
    'gagan': 'https://upload.wikimedia.org/wikipedia/commons/2/29/Gagan_Thapa_%E0%A4%97%E0%A4%97%E0%A4%A8_%E0%A4%A5%E0%A4%BE%E0%A4%AA%E0%A4%BE_Member_of_Parliament%2C_Pratinidhi_Sabha_%28cropped%29.jpg',
    'durga': 'https://upload.wikimedia.org/wikipedia/commons/b/ba/Nava_Raj_Subedi_%E0%A4%A8%E0%A4%B5%E0%A4%B0%E0%A4%BE%E0%A4%9C_%E0%A4%B8%E0%A5%81%E0%A4%B5%E0%A5%87%E0%A4%A6%E0%A5%80_And_%E0%A4%A6%E0%A5%81%E0%A4%B0%E0%A5%8D%E0%A4%97%E0%A4%BE_%E0%A4%AA%E0%A5%8D%E0%A4%B0%E0%A4%B8%E0%A4%BE%E0%A4%88_Durga_Prasai_%E0%A4%B0%E0%A4%BE%E0%A4%9C%E0%A4%BE%E0%A4%AC%E0%A4%BE%E0%A4%A6%E0%A5%80.png',
    'genz': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Rabi_Lamichhane.png/800px-Rabi_Lamichhane.png'
}

os.makedirs('public/faces', exist_ok=True)

def crop_face_square(img):
    w, h = img.size
    min_dim = min(w, h)
    if h > w:
        top = int((h - w) * 0.10)
        return img.crop((0, top, w, top + w))
    else:
        left = int((w - h) * 0.5)
        return img.crop((left, 0, left + h, h))

for name, url in URLS.items():
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        raw_path = f'raw_{name}.jpg'
        with urllib.request.urlopen(req, timeout=15) as resp, open(raw_path, 'wb') as f:
            f.write(resp.read())
            
        im = Image.open(raw_path).convert('RGB')
        sq = crop_face_square(im).resize((1024, 1024), Image.LANCZOS)
        out_webp = f'public/faces/{name}.webp'
        sq.save(out_webp, 'WEBP', quality=95)
        print(f'Saved {out_webp} ({os.path.getsize(out_webp)} bytes)')
        if os.path.exists(raw_path):
            os.remove(raw_path)
    except Exception as e:
        print(f'Error for {name}: {e}')
