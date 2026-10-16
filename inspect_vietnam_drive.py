import requests
import re
import json

url = 'https://drive.google.com/drive/folders/1A8FMkO34ubApwXKmzA4dX4D0Njv16cXK'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
r = requests.get(url, headers=headers)

with open('vietnam_drive.html', 'w', encoding='utf-8') as f:
    f.write(r.text)

print('Drive HTML saved, size:', len(r.text))

# Search for filenames
filenames = re.findall(r'([a-zA-Z0-9_ -]+\.(?:pdf|png|jpg|jpeg|ai|psd|svg|pptx|ppt|docx|doc))', r.text, re.IGNORECASE)
print('Unique filenames found in Vietnam designer / Branding folder:', len(set(filenames)))
for fn in sorted(set(filenames)):
    print(' -', fn)

# Extract file items
# Look for: [\"ID\",[\"Filename\"
items = re.findall(r'\["([a-zA-Z0-9_-]{28,35})",\["([^"]+)"', r.text)
print(f"Direct ID -> Name matches ({len(items)}):")
for item_id, name in items:
    print(f"  {item_id} -> {name}")
