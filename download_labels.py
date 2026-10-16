import os
import requests

FILES = {
    # Top Lid Labels
    "Anhialo Massage Gel_Arnica Top Fv17.pdf": "1OlcVL4S-REIR-R31JjFuEDGpcVi6nxyU",
    "Anhialo Massage Gel_Grape Top Fv17.pdf": "1ngajYjt8ahEZOHEULfUgaSJgg6dkDP0P",
    "Anhialo Massage Gel_Juniper Top Fv17.pdf": "1ZwZeuUY0MxDTlNR7i1T_iYzYPdNTeKiM",
    "Anhialo Massage Gel_Lavender Top Fv17.pdf": "1W1WfFN3C2QfZ7XZZQ4lW8dU_IrSY7ebr",
    "Anhialo Massage Gel_Rosemary Top Fv17.pdf": "1XxNXGqX94STlNZD1n-Ca_2GXPEJpGeeP",
    # Side Jar Labels
    "Side Label Grey Arnica v12.pdf": "1DrMd7ov-phTJX-QL1G8MXhqljyQxFbSY",
    "Side Label Grey Grape v12.pdf": "1cpQQYx2bYLnS_eAkejL3PSsW7Ijnz_vp",
    "Side Label Grey Juniper v12.pdf": "1f-fRDIHvU40t1VzJXJEPa00AnlCdfTSE",
    "Side Label Grey Lavender v12.pdf": "1N5NS1-lQqbrkbXEHf31BY-u8m-R8u8Rd",
    "Side Label Grey Rosemary v12.pdf": "1p32MFnA4pCPtUv4hZZmQ6YwckZm0Omo_"
}

output_dir = os.path.join(os.path.dirname(__file__), "labels", "original")
os.makedirs(output_dir, exist_ok=True)

print(f"Downloading {len(FILES)} label PDFs to {output_dir}...")

for filename, file_id in FILES.items():
    dest_path = os.path.join(output_dir, filename)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 100000:
        print(f"Skipping already downloaded: {filename} ({os.path.getsize(dest_path)} bytes)")
        continue
    
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    print(f"Downloading: {filename}...")
    r = requests.get(url, allow_redirects=True, timeout=60)
    if r.status_code == 200 and r.content.startswith(b"%PDF"):
        with open(dest_path, "wb") as f:
            f.write(r.content)
        print(f"  ✓ Saved: {filename} ({len(r.content):,} bytes)")
    else:
        print(f"  ✗ Failed ({r.status_code}): {filename}")

print("\nAll label downloads completed.")
