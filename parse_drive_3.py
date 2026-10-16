from bs4 import BeautifulSoup
import re
import json

with open('drive_folder_3.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
scripts = soup.find_all('script')

print(f"Total scripts: {len(scripts)}")

for i, s in enumerate(scripts):
    txt = s.text
    if len(txt) > 2000:
        # Search for file extensions or file titles
        # In Google Drive initial state, files are in JSON arrays like ["filename.ext", ...
        matches = re.findall(r'\["([a-zA-Z0-9_-]{28,35})",\["([^"]+)"', txt)
        if matches:
            print(f"Script {i} has {len(matches)} direct item matches:")
            for item_id, name in matches:
                print(f"  {item_id} -> {name}")
                
        # Also general title search
        items = re.findall(r'"([^"\\]+\.(?:pdf|png|jpg|jpeg|docx|ai|psd|svg|tif|cdr|eps))"', txt, re.IGNORECASE)
        filtered = [x for x in set(items) if not x.startswith('google') and not x.startswith('logo') and not x.startswith('drive')]
        if filtered:
            print(f"Script {i} candidate files ({len(filtered)}):")
            for fn in sorted(filtered):
                print(f"  - {fn}")

# Check if the folder requires login or is empty or has subfolders
if "Authentication" in html or "Sign in" in html:
    print("Warning: Sign in detected or permission needed")
