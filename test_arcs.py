import fitz

svg = """<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
  <defs>
    <path id="topArc" d="M 80,300 A 220,220 0 0,1 520,300" fill="none"/>
    <path id="bottomArc" d="M 520,300 A 220,220 0 0,1 80,300" fill="none"/>
    <path id="bottomArcUpright" d="M 80,300 A 220,220 0 0,0 520,300" fill="none"/>
  </defs>
  <circle cx="300" cy="300" r="280" fill="#FFF" stroke="#C5A059" stroke-width="3"/>
  <text font-family="sans-serif" font-size="16" font-weight="bold">
    <textPath href="#topArc" startOffset="50%" text-anchor="middle">
      MAGNESIUM CHLORIDE &amp; MAGNESIUM SULFATE
    </textPath>
  </text>
  <text font-family="sans-serif" font-size="16" font-weight="bold" fill="blue">
    <textPath href="#bottomArcUpright" startOffset="50%" text-anchor="middle">
      NATURAL TOPICAL GEL · BLACK SEA LYE 300g
    </textPath>
  </text>
</svg>"""

with open("test_arcs.svg", "w", encoding="utf-8") as f:
    f.write(svg)

doc = fitz.open("test_arcs.svg")
pix = doc[0].get_pixmap()
pix.save("test_arcs.png")
print("Saved test_arcs.png")
