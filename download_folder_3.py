import os
import requests

FILES = {
    "ANCHIALO Masazhno maslo_от черноморска луга.jpg": "1pCzfhgqKlWIVLAbJIrSaMKF_I3r7HFnn",
    "ANCHIALO Masazhno maslo_с арника.jpg": "1pt3MruSFkCZDAMiSLVwR3wwSKQ7wfltK",
    "ANCHIALO Masazhno maslo_с лавандула.jpg": "1lmVtHDQsyM9Rmqc1HEJzMCpndkAqExHc",
    "ANCHIALO Masazhno maslo_с розмарин.jpg": "1Wj7nDWvF1F0zdD5Jo4OYSEh0Jj25M8Lh",
    "ANCHIALO Masazhno maslo_с хвойна.jpg": "1LMyjjM04k6rARbBGKwReIw4cEJflB78y",
    "Anhialo Massage Gel (1).pdf": "1IudbC41Y4KOXRiuOLN14P22gI8jlxooU",
    "Masazhen gel 300 g 159x38 mm_Lavandula (1).jpg": "1mjvIW3pbZKMAfxVyvPayXZnygkfTJfII",
    "Masazhen gel 300 g 159x38 mm_с Арника (4).jpg": "1mDOxakvJyu7fTrOaAjQVsCAivSCh8-nA",
    "Masazhen gel 300 g 159x38 mm_с розамарин.jpg": "1WioLnAqVbSReG3NBEhwOSnwd6VCDWpsI",
    "Masazhen gel 300 g 159x38 mm_с черноморска луга (5).jpg": "1pzpH6jPd_X61G7aljyZdFS25RoWw33II"
}

dest_dir = os.path.join(os.path.dirname(__file__), "labels", "folder_3")
os.makedirs(dest_dir, exist_ok=True)

print(f"Downloading {len(FILES)} assets from 3rd Google Drive folder...")

for name, fid in FILES.items():
    path = os.path.join(dest_dir, name)
    url = f"https://drive.google.com/uc?export=download&id={fid}"
    print(f"Downloading: {name}...")
    try:
        r = requests.get(url, allow_redirects=True, timeout=60)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            print(f"  ✓ Saved {name} ({len(r.content):,} bytes)")
        else:
            print(f"  ✗ Status {r.status_code} for {name}")
    except Exception as e:
        print(f"  ✗ Error for {name}: {e}")

print("All downloads finished.")
