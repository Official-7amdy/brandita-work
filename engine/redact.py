"""Burns redactions into evidence screenshots.

Reads the unredacted originals from BD-Assets/_private/evidence-originals (never
published) and writes redacted copies to interactive/img. Each box in a case
file's "evidence[].hide" is painted solid, so nothing under it can be recovered
from the published image.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PRIVATE = os.path.normpath(os.path.join(HERE, "..", "..", "_private", "evidence-originals"))
OUT = os.path.normpath(os.path.join(HERE, "..", "img"))

def _font(size):
    for name in ("arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()

def redact(file, boxes):
    src = os.path.join(PRIVATE, file)
    if not os.path.exists(src):
        raise FileNotFoundError(f"original missing: {src}")
    im = Image.open(src).convert("RGB")
    d = ImageDraw.Draw(im)
    for b in boxes:
        x, y, w, h = b["x"], b["y"], b["w"], b["h"]
        r = min(8, h // 3)
        d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=(20, 19, 22), outline=(64, 61, 68), width=1)
        label = (b.get("label") or "").upper()
        if label and w >= 60 and h >= 18:
            f = _font(max(10, min(14, h // 3)))
            text = f"HIDDEN · {label}" if w >= 120 else "HIDDEN"
            tw = d.textlength(text, font=f)
            if tw > w - 10:
                text = "HIDDEN"; tw = d.textlength(text, font=f)
            d.text((x + (w - tw) / 2, y + h / 2), text, font=f, fill=(170, 165, 175), anchor="lm")
    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, file)
    im.save(dst, optimize=True)
    return dst

def redact_case(case):
    done = []
    for ev in case.get("evidence", []):
        done.append(redact(ev["file"], ev.get("hide", [])))
    return done

if __name__ == "__main__":
    import json, glob, sys
    for path in sorted(glob.glob(os.path.join(HERE, "cases", "*.json"))):
        with open(path, encoding="utf-8") as fh:
            case = json.load(fh)
        for out in redact_case(case):
            print("redacted", os.path.basename(out))
