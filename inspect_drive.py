import requests
import re
import json

url = 'https://drive.google.com/drive/folders/1m4gfKZRRaqbV4CFtrYD-AdDJocNEd667'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
r = requests.get(url, headers=headers)

with open('drive_page.html', 'w', encoding='utf-8') as f:
    f.write(r.text)

print('Drive HTML saved, size:', len(r.text))

# Search for patterns in Google Drive's initial data
# Drive embeds item data in JS array format
# e.g. ["file_id", ["file_name.pdf", ...], ...]
items = re.findall(r'\["([a-zA-Z0-9_-]{28,35})",\["([^"]+)"', r.text)
print('Found items:', len(items))
for item_id, name in items:
    print(f"ID: {item_id} -> Name: {name}")

# Also search for filenames ending in common graphic/label formats
filenames = re.findall(r'([a-zA-Z0-9_ -]+\.(?:pdf|png|jpg|jpeg|ai|psd|svg|tif|cdr|eps))', r.text, re.IGNORECASE)
print('Unique filenames found:', len(set(filenames)))
for fn in sorted(set(filenames)):
    print(" -", fn)
