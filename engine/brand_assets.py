"""Web assets from the brand files in BD-Assets/brand-drive (the designer's exports).

    python brand_assets.py      # writes interactive/brand/*.png and brand/brand.json

- Wordmarks (English and Arabic, black and white) trimmed to the mark and sized
  for the header at 3x. The marks are only scaled, never recoloured.
- The B. monogram and the B. Team signature come on a #131313 square; they are
  lifted off it (alpha from the known ground) so they sit on any dark surface.
- Favicons are the monogram square as delivered.
- brand.json holds the data URIs the single-file pages embed.
"""
import base64, io, json, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "brand-drive")
OUT = os.path.join(HERE, "brand")
os.makedirs(OUT, exist_ok=True)
INK, BONE, RED = (0x13, 0x13, 0x13), (0xF5, 0xF4, 0xF1), (0xD6, 0x32, 0x33)

def trim(im):
    return im.crop(im.getbbox())

def height(im, h):
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)

def lift(im):
    """the mark was drawn on flat INK: recover each pixel's alpha against that ground"""
    im = im.convert("RGB")
    px = im.load(); out = Image.new("RGBA", im.size); po = out.load()
    for y in range(im.height):
        for x in range(im.width):
            p = px[x, y]
            fg = RED if p[0] - p[1] > 40 else BONE  # the dot and the script are red, the letters bone
            a = max(0.0, min(1.0, max((p[i] - INK[i]) / (fg[i] - INK[i]) for i in range(3) if fg[i] != INK[i])))
            po[x, y] = (*fg, round(a * 255)) if a > 0.02 else (0, 0, 0, 0)
    return out

def save(im, name):
    p = os.path.join(OUT, name); im.save(p, optimize=True); return p

def uri(p):
    with open(p, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

assets = {}
for key, f in {"wm_en_black": "logos/png/Logos-01.png", "wm_en_white": "logos/png/Logos-02.png",
               "wm_ar_black": "logos/png/Logos-03.png", "wm_ar_white": "logos/png/Logos-04.png"}.items():
    im = height(trim(Image.open(os.path.join(SRC, f)).convert("RGBA")), 72)
    assets[key] = {"uri": uri(save(im, key.replace("_", "-") + ".png")), "w": im.width, "h": im.height}

# the oversized sign-off mark in the footer, sharp at full page width
for key, f in {"wm_en_white_xl": "logos/png/Logos-02.png", "wm_ar_white_xl": "logos/png/Logos-04.png"}.items():
    im = height(trim(Image.open(os.path.join(SRC, f)).convert("RGBA")), 300)
    assets[key] = {"uri": uri(save(im, key.replace("_", "-") + ".png")), "w": im.width, "h": im.height}

mono_sq = Image.open(os.path.join(SRC, "B Logo.png")).convert("RGB")
small = mono_sq.resize((1125, 1125), Image.LANCZOS)  # lift at a working size, then scale
mono = trim(lift(small))
for k, size in (("mono", 160),):
    m = height(mono, size); assets[k] = {"uri": uri(save(m, "mono.png")), "w": m.width, "h": m.height}
for k, s in (("icon32", 32), ("icon180", 180)):
    assets[k] = {"uri": uri(save(mono_sq.resize((s, s), Image.LANCZOS), f"{k}.png")), "w": s, "h": s}

team = Image.open(os.path.join(SRC, "Brandita Team.png")).convert("RGB").resize((1125, 1125), Image.LANCZOS)
sig = height(trim(lift(team)), 150)
assets["sig"] = {"uri": uri(save(sig, "sig.png")), "w": sig.width, "h": sig.height}

with open(os.path.join(OUT, "brand.json"), "w", encoding="utf-8") as f:
    json.dump({"colors": {"ink": "#131313", "bone": "#F5F4F1", "paper": "#EEEDED", "red": "#D63233"}, **assets}, f)
for k, v in assets.items():
    print(k, v["w"], "x", v["h"], round(len(v["uri"]) / 1024), "KB")
