"""Moves the web pages onto the new brand files (run brand_assets.py first).

    python rebrand.py

Palette from the designer's exports: ink #131313, bone #F5F4F1, paper #EEEDED,
red #D63233 (the dot). The old lavender-tinted greys become neutral greys.
Every embedded wordmark is swapped for the new one of the same tone (black on
light, white on dark), the monogram becomes the site icon and the case loader,
and the booking section is signed with the B. Team mark. Safe to run again.
"""
import base64, io, json, os, re
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
B = json.load(open(os.path.join(HERE, "brand", "brand.json"), encoding="utf-8"))
WM_RATIO = B["wm_en_white"]["w"] / B["wm_en_white"]["h"]

PALETTE = [  # old -> new, case-insensitive hex; client palettes in the pages use none of these
    ("#0B0B0B", "#131313"), ("#060606", "#0E0E0E"), ("#151416", "#1B1B1B"), ("#1E1C1F", "#222222"), ("#2A282D", "#262626"),
    ("#2A282C", "#2A2A2A"), ("#4A464D", "#4A4A4A"), ("#131114", "#131313"), ("#141315", "#161616"), ("#1B181C", "#1B1B1B"),
    ("#1E1B1F", "#1F1F1F"), ("#A49FA6", "#A3A29F"), ("#E6DCEA", "#D9D8D6"), ("#F7F2F8", "#F5F4F1"), ("#F5EFF6", "#F5F4F1"),
    ("#FEF7FF", "#EEEDED"), ("#F5EAF7", "#E4E3E2"), ("#DE0000", "#D63233"), ("#E33232", "#D63233"), ("#F5342E", "#D63233"),
]
RGBA = [("rgba(247,242,248", "rgba(245,244,241"), ("rgba(247, 242, 248", "rgba(245, 244, 241"), ("rgba(16,15,18", "rgba(19,19,19"),
        ("rgba(22,21,24", "rgba(19,19,19"), ("rgba(12,11,13", "rgba(14,14,14"), ("rgba(58,56,62", "rgba(58,58,58")]

def recolour(t):
    for a, b in PALETTE:
        t = re.sub(re.escape(a), b, t, flags=re.I)
    for a, b in RGBA:
        t = t.replace(a, b)
    return t

def swap_wordmarks(t):
    """any embedded image that is a Brandita wordmark becomes the new one of the same tone"""
    def one(m):
        pre, data, post = m.group(1), m.group(2), m.group(3)
        try:
            im = Image.open(io.BytesIO(base64.b64decode(data))).convert("RGBA")
        except Exception:
            return m.group(0)
        if not (2.2 < im.width / im.height < 5.5) or data in (B["wm_en_white"]["uri"][22:], B["wm_en_black"]["uri"][22:]):
            return m.group(0)  # not a wordmark, or already new
        px = [p for p in im.resize((60, 18)).getdata() if p[3] > 200 and not (p[0] > 150 and p[1] < 90)]
        light = sum(p[0] for p in px) / max(1, len(px)) > 128
        new = B["wm_en_white" if light else "wm_en_black"]["uri"]
        tag = pre + new + post
        h = re.search(r'height="(\d+)"', tag)
        if h:
            tag = re.sub(r'width="\d+"', f'width="{round(int(h.group(1)) * WM_RATIO)}"', tag)
        return tag
    return re.sub(r'(<img[^>]*?src=")data:image/png;base64,([A-Za-z0-9+/=]+)("[^>]*>)', lambda m: one(m), t)

ICONS = (f'<link rel="icon" type="image/png" sizes="32x32" href="{B["icon32"]["uri"]}">\n'
         f'<link rel="apple-touch-icon" href="{B["icon180"]["uri"]}">\n')

def icons(t):
    if 'rel="icon"' in t:
        return t
    return re.sub(r"(<title>[^<]*</title>\n?)", lambda m: m.group(1) + ICONS, t, count=1)

def rw(name, fn):
    p = os.path.join(HERE, name)
    with open(p, encoding="utf-8", newline="") as f:
        t = f.read()
    CR, LF = chr(13), chr(10)
    crlf = CR + LF in t
    t = t.replace(CR + LF, LF)
    n = fn(t)
    if n != t:
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(n.replace(LF, CR + LF) if crlf else n)
    print(("updated " if n != t else "unchanged ") + name)

# ── the case studies page ────────────────────────────────────────────────
def page(t):
    t = icons(swap_wordmarks(recolour(t)))
    # the header wordmark box takes the new proportions
    t = t.replace(".wmlink{position:relative;display:block;width:76px;height:23px}", f".wmlink{{position:relative;display:block;width:{round(20 * WM_RATIO)}px;height:20px}}")
    t = re.sub(r'(class="wm [bw]" src="[^"]+" alt="[^"]*") width="\d+" height="\d+"', lambda m: m.group(1) + f' width="{round(20 * WM_RATIO)}" height="20"', t)
    t = t.replace(".site-foot .brand img{display:block;height:27px;width:auto}", ".site-foot .brand img{display:block;height:30px;width:auto}")
    # opening a case: the monogram holds the sheet while the case loads
    if 'class="dload-m"' not in t:
        t = t.replace('<div class="dload" aria-hidden="true"><span></span></div>',
                      f'<div class="dload" aria-hidden="true"><img class="dload-m" src="{B["mono"]["uri"]}" alt="" width="{B["mono"]["w"] // 3}" height="{B["mono"]["h"] // 3}"><span></span></div>')
        t = t.replace(".dload{position:absolute;inset:0;display:grid;place-items:center;pointer-events:none}",
                      ".dload{position:absolute;inset:0;display:grid;place-content:center;justify-items:center;gap:22px;pointer-events:none}\n"
                      ".dload-m{display:block;width:47px;height:auto;animation:dl-in .6s cubic-bezier(.23,1,.32,1) both}\n"
                      "@keyframes dl-in{from{opacity:0;transform:translateY(8px) scale(.94)}}")
        t = t.replace(".dload span{width:34px;height:34px;border-radius:50%;border:3px solid rgba(255,255,255,.2);border-top-color:#fff;animation:spin 1s linear infinite}",
                      ".dload span{width:64px;height:2px;border-radius:2px;background:rgba(255,255,255,.14);position:relative;overflow:hidden}\n"
                      ".dload span::after{content:\"\";position:absolute;inset:0;width:40%;background:#D63233;animation:dl-run 1.1s cubic-bezier(.65,0,.35,1) infinite}\n"
                      "@keyframes dl-run{from{transform:translateX(-100%)}to{transform:translateX(250%)}}")
    # the booking section is signed by the team
    if 'class="sig"' not in t:
        t = t.replace('</a>\n      </div>\n      <ul class="sheet"',
                      f'</a>\n        <img class="sig" src="{B["sig"]["uri"]}" alt="Brandita team" width="{B["sig"]["w"] // 2}" height="{B["sig"]["h"] // 2}">\n      </div>\n      <ul class="sheet"', 1)
        t = t.replace(".close{padding-top:", ".close .sig{display:block;width:92px;height:auto;margin-top:34px}\n.close{padding-top:", 1)
    return t

rw("case-studies.html", page)
rw("case-engine/engine.css", recolour)
rw("ecommerce-landing.html", lambda t: icons(swap_wordmarks(recolour(t))))
rw("client-case.html", lambda t: icons(swap_wordmarks(recolour(t))))

# case pages get the icon from the builder
def builder(t):
    if "ICONS = " in t:
        return t
    t = t.replace('STORIES = "https://claude.ai/artifact/GUMuDPecfJkTZaLWBaaiud"',
                  'STORIES = "https://claude.ai/artifact/GUMuDPecfJkTZaLWBaaiud"\n'
                  '_B = json.load(open(os.path.join(INTERACTIVE, "brand", "brand.json"), encoding="utf-8"))\n'
                  'ICONS = f\'<link rel="icon" type="image/png" sizes="32x32" href="{_B["icon32"]["uri"]}">\\n<link rel="apple-touch-icon" href="{_B["icon180"]["uri"]}">\'')
    return t.replace("<title>{title}</title>\n", "<title>{title}</title>\n{ICONS}\n")
rw("case-engine/build_cases.py", builder)
