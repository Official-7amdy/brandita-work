"""Brandita case builder.

    python build_cases.py            # build every case in cases/
    python build_cases.py lazoomi    # build one

For each case file it: checks the file (a real client needs approved: true;
series totals must match their rows), burns the screenshot redactions, and
writes interactive/case-<id>.html, a page the engine renders from the file.
Run build-site.ps1 afterwards to publish into site/.
"""
import json, os, re, sys
from redact import redact_case

HERE = os.path.dirname(os.path.abspath(__file__))
INTERACTIVE = os.path.dirname(HERE)
ORDER = ["lazoomi", "speed", "arabic", "media", "seo", "checkout", "replies", "identity", "ramadan"]
# artifact links; build-site.ps1 maps them to relative pages on the website
STORIES = "https://claude.ai/artifact/GUMuDPecfJkTZaLWBaaiud"
BOOK = "https://claude.ai/artifact/Ny51PSz3Cb51nps8m1j7D6#start"

class CaseError(Exception):
    pass

def check(c):
    for k in ("id", "client", "sector", "line", "headline", "metric", "palette"):
        if not c.get(k):
            raise CaseError(f"{c.get('id', '?')}: missing '{k}'")
    if c.get("real") and c.get("approved") is not True:
        raise CaseError(f"{c['id']}: a real client is published only with written approval (set approved: true)")
    s = c.get("series")
    if s:
        rows, tot = s["rows"], s.get("totals", {})
        if len(rows) != len(s["months"]):
            raise CaseError(f"{c['id']}: {len(rows)} series rows for {len(s['months'])} months")
        for k in ("orders", "spend", "sales"):
            if k in tot and abs(sum(r[k] for r in rows) - tot[k]) > max(1, tot[k] * 0.001):
                raise CaseError(f"{c['id']}: series {k} rows add up to {sum(r[k] for r in rows):,.2f}, totals say {tot[k]:,.2f}")
    for ev in c.get("evidence", []):
        for b in ev.get("hide", []):
            if min(b["w"], b["h"]) <= 0:
                raise CaseError(f"{c['id']}: empty redaction box on {ev['file']}")

def logo(html):
    m = re.search(r'class="wm w" src="(data:image/png;base64,[^"]+)"', html)
    return m.group(1) if m else ""

def page(c, engine_js, engine_css, logo_uri, nxt):
    opts = {"bookUrl": BOOK, "storiesUrl": STORIES, "logo": logo_uri,
            "next": {"href": f"case-{nxt['id']}.html", "title": nxt["client"], "headline": nxt["headline"], "metric": nxt["metric"]["value"],
                     "bg": nxt["palette"]["bg"], "fg": nxt["palette"]["fg"], "accent": nxt["palette"]["accent"]} if nxt else None}
    data = json.dumps(c, ensure_ascii=False).replace("</", "<\\/")
    title = f"{c['client']} case study · Brandita"
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Cairo:wght@600;800&display=swap">
<style>
html,body{{margin:0;background:{c['palette']['bg']}}}
{engine_css}
</style>
<div id="case"></div>
<script>
{engine_js}
</script>
<script>
(function () {{
  var q = new URLSearchParams(location.search), opts = {json.dumps(opts)};
  opts.embed = q.has("embed");
  window.CASE = {data};
  CaseEngine.render(window.CASE, document.getElementById("case"), opts);
}})();
</script>
"""

def main(only=None):
    with open(os.path.join(HERE, "engine.js"), encoding="utf-8") as f: engine_js = f.read()
    with open(os.path.join(HERE, "engine.css"), encoding="utf-8") as f: engine_css = f.read()
    with open(os.path.join(INTERACTIVE, "case-studies.html"), encoding="utf-8") as f: logo_uri = logo(f.read())
    cases = {}
    for fn in os.listdir(os.path.join(HERE, "cases")):
        if fn.endswith(".json"):
            with open(os.path.join(HERE, "cases", fn), encoding="utf-8") as f:
                c = json.load(f); cases[c["id"]] = c
    ids = [i for i in ORDER if i in cases] + sorted(i for i in cases if i not in ORDER)
    for i in ids: check(cases[i])
    for n, i in enumerate(ids):
        if only and i != only: continue
        c = cases[i]
        redact_case(c)
        out = os.path.join(INTERACTIVE, f"case-{i}.html")
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(page(c, engine_js, engine_css, logo_uri, cases[ids[(n + 1) % len(ids)]]))
        print(f"built case-{i}.html{' (sample)' if not c.get('real') else ''}")

if __name__ == "__main__":
    try:
        main(sys.argv[1] if len(sys.argv) > 1 else None)
    except CaseError as e:
        sys.exit("case file rejected: " + str(e))
