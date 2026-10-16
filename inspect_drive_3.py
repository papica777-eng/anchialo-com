import requests
import re
import json

url = 'https://drive.google.com/drive/folders/1h8krD-riOSujINV4GvNrm82kruY3UJxB'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
r = requests.get(url, headers=headers)

with open('drive_folder_3.html', 'w', encoding='utf-8') as f:
    f.write(r.text)

print('Drive HTML saved, size:', len(r.text))

# Search for filenames
filenames = re.findall(r'([a-zA-Z0-9_ -]+\.(?:pdf|png|jpg|jpeg|ai|psd|svg|pptx|ppt|docx|doc|zip|rar))', r.text, re.IGNORECASE)
unique_fn = sorted(set(filenames))
print(f'Unique filenames found in 3rd folder ({len(unique_fn)}):')
for fn in unique_fn:
    print(' -', fn)

# Find candidate IDs for these files
for fn in unique_fn:
    if fn.endswith(('.pdf', '.ai', '.psd', '.png', '.jpg', '.jpeg', '.docx', '.zip')):
        pos = r.text.find(fn)
        if pos != -1:
            snippet = r.text[max(0, pos-250):min(len(r.text), pos+250)]
            ids = [x for x in re.findall(r'[a-zA-Z0-9_-]{28,35}', snippet) if not x.startswith('data-')]
            print(f"File: {fn} -> IDs: {ids}")
