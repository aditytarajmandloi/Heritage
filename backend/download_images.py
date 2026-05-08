import urllib.request
import os

images = {
    "taj_mahal.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Taj_Mahal_%28Edited%29.jpg/800px-Taj_Mahal_%28Edited%29.jpg",
    "red_fort.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Red_Fort_in_Delhi_03.jpg/800px-Red_Fort_in_Delhi_03.jpg",
    "gateway_of_india.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Mumbai_03-2016_30_Gateway_of_India.jpg/800px-Mumbai_03-2016_30_Gateway_of_India.jpg",
    "hawa_mahal.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Hawa_Mahal_2011.jpg/800px-Hawa_Mahal_2011.jpg",
    "mysore_palace.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Mysore_Palace_Morning.jpg/800px-Mysore_Palace_Morning.jpg"
}

out_dir = "static/images"
os.makedirs(out_dir, exist_ok=True)

for name, url in images.items():
    path = os.path.join(out_dir, name)
    print(f"Downloading {name}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
    except Exception as e:
        print(f"Failed to download {name}: {e}")
