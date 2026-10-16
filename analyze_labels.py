import os
import re

labels_dir = os.path.join(os.path.dirname(__file__), "labels", "original")

def inspect_pdf(filepath):
    print(f"\n==========================================")
    print(f"FILE: {os.path.basename(filepath)}")
    print(f"SIZE: {os.path.getsize(filepath):,} bytes")
    with open(filepath, "rb") as f:
        data = f.read()
    
    # Extract visible strings (ASCII / basic UTF-16)
    strings = []
    # Search for Text operators in streams: (Text) Tj or [(T) (e) (x) (t)] TJ
    raw_texts = re.findall(rb'\((.*?)\)\s*Tj', data)
    for rt in raw_texts:
        try:
            s = rt.decode('latin1', errors='ignore')
            if len(s.strip()) > 1:
                strings.append(s.strip())
        except Exception:
            pass
    
    # Also look for Creator / Producer / Info
    info_matches = re.findall(rb'/(?:Title|Author|Creator|Producer|Subject)\s*\((.*?)\)', data)
    print("PDF Metadata:", [m.decode('latin1', errors='ignore') for m in info_matches])
    
    # Deduplicate and display top readable strings
    unique_strings = []
    for s in strings:
        if s not in unique_strings and len(s) > 2:
            unique_strings.append(s)
            
    print(f"Extracted Text Strings ({len(unique_strings)} found):")
    for s in unique_strings[:30]:
        print("  -", s)

for f in sorted(os.listdir(labels_dir)):
    if f.endswith(".pdf"):
        inspect_pdf(os.path.join(labels_dir, f))
