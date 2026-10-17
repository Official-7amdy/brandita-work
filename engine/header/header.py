"""One header on every Brandita page.

    python header/header.py

bh.css and bh.js are the single source. This script writes them into each
page between markers (/* bh:css */ ... /* /bh:css */, /* bh:js */ ... /* /bh:js */)
and renders the header markup from one template (<!-- bh --> ... <!-- /bh -->),
so the pages cannot drift apart again. Pages migrated the first time are
also cleaned of their old header CSS and markup. Safe to run again.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSS = open(os.path.join(HERE, "bh.css"), encoding="utf-8").read().strip()
JS = open(os.path.join(HERE, "bh.js"), encoding="utf-8").read().strip()
FCSS = open(os.path.join(HERE, "bf.css"), encoding="utf-8").read().strip()
B = json.load(open(os.path.join(ROOT, "brand", "brand.json"), encoding="utf-8"))
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>'
AR_URL, EN_URL = "https://claude.ai/artifact/C1uxFXVECptuqe8ki74juS", "https://claude.ai/artifact/GUMuDPecfJkTZaLWBaaiud"
WM_H = 20
WM_W = round(WM_H * B["wm_en_white"]["w"] / B["wm_en_white"]["h"])


def header(home, mid="", mid_keep=False, tick="dot", tick_text="", lang="", cta_href="#start", cta_label="Book a call", tone="dark", tag="Digital marketing · Cairo", attrs=None, space=False):
    """the markup every page uses; only the slots differ"""
    t = (f'<i class="bh-{tick}" aria-hidden="true"></i>' if tick else "") + f'<span class="bh-tx">{tick_text}</span>'
    extra = "".join(f' data-{k}="{v}"' for k, v in (attrs or {}).items())
    return (f'<!-- bh -->\n<header class="bh" id="bh" data-tone="{tone}"{extra}>\n  <div class="bh-bar">\n'
            f'    <div class="bh-start"><a class="bh-logo" href="{home}" aria-label="Brandita, home">'
            f'<img class="w" src="{B["wm_en_white"]["uri"]}" alt="Brandita" width="{WM_W}" height="{WM_H}">'
            f'<img class="k" src="{B["wm_en_black"]["uri"]}" alt="" width="{WM_W}" height="{WM_H}"></a>'
            + (f'<span class="bh-tag">{tag}</span>' if tag else "") + '</div>\n'
            f'    <nav class="bh-mid{" keep" if mid_keep else ""}" id="views" aria-label="Main">{mid}</nav>\n'
            f'    <div class="bh-end"><span class="bh-tick" aria-live="polite">{t}</span>{lang}'
            f'<a class="bh-cta" href="{cta_href}" data-cursor="Book"><span>{cta_label}</span><i aria-hidden="true">{ARROW}</i></a></div>\n'
            '  </div>\n</header>\n'
            f'<script>\n/* bh:js */\n{JS}\n/* /bh:js */\n</script>\n' + ('<div class="bh-space" aria-hidden="true"></div>\n' if space else "") + '<!-- /bh -->')


def sync(t):
    """refresh the shared CSS/JS blocks in a page that already has them"""
    t = re.sub(r"/\* bh:css \*/.*?/\* /bh:css \*/", lambda m: f"/* bh:css */\n{CSS}\n/* /bh:css */", t, flags=re.S)
    t = re.sub(r"/\* bh:js \*/.*?/\* /bh:js \*/", lambda m: f"/* bh:js */\n{JS}\n/* /bh:js */", t, flags=re.S)
    if "/* bf:css */" not in t and "/* /bh:css */" in t:  # the footer travels with the header
        t = t.replace("/* /bh:css */", f"/* /bh:css */\n/* bf:css */\n{FCSS}\n/* /bf:css */", 1)
    t = re.sub(r"/\* bf:css \*/.*?/\* /bf:css \*/", lambda m: f"/* bf:css */\n{FCSS}\n/* /bf:css */", t, flags=re.S)
    return t


SOCIAL = [("LinkedIn", "https://linkedin.com/company/brandita"), ("Instagram", "https://instagram.com/brandita"),
          ("Facebook", "https://facebook.com/brandita"), ("TikTok", "https://tiktok.com/@brandita")]
STORES_URL, CLIENT_URL = "https://claude.ai/artifact/Ny51PSz3Cb51nps8m1j7D6", "https://claude.ai/artifact/6zCn3cMvHCzk9erCcx5T1C"

def footer(stories, studies, book, top="#top", lang=""):
    """the footer every page uses; the links point within the page where they can"""
    li = lambda items: "".join(f'<li><a href="{h}"{x}>{l}</a></li>' for l, h, x in items)
    out = ' target="_blank" rel="noopener"'
    return ('<!-- bf -->\n<footer class="bf">\n  <div class="bf-in">\n    <div class="bf-top">\n'
            f'      <div class="bf-brand"><img src="{B["wm_en_white"]["uri"]}" alt="Brandita" width="{round(22 * WM_W / WM_H)}" height="22">'
            '<p>A digital marketing agency in Cairo: brand and creative, performance media, social and community, SEO and content.</p></div>\n'
            '      <nav class="bf-col" aria-labelledby="bf-w"><h2 id="bf-w">Work</h2><ul>'
            + li([("Case stories", stories, ""), ("Case studies", studies, ""), ("For online stores", STORES_URL, ""), ("A full client case", CLIENT_URL, "")]) + '</ul></nav>\n'
            '      <nav class="bf-col" aria-labelledby="bf-c"><h2 id="bf-c">Contact</h2><ul>'
            + li([("info@brandita.net", "mailto:info@brandita.net", ""), ("WhatsApp", "https://wa.me/201099307190", out), ("Book a call", book, "")]) + '</ul></nav>\n'
            '      <nav class="bf-col" aria-labelledby="bf-f"><h2 id="bf-f">Follow</h2><ul>' + li([(l, h, out) for l, h in SOCIAL]) + '</ul></nav>\n'
            '    </div>\n'
            '    <div class="bf-base"><span>© 2026 All rights reserved — Brandita.net | Cairo, Egypt | info@brandita.net</span>'
            f'<span class="bf-meta">{lang}<a href="{top}">Back to top <span aria-hidden="true">↑</span></a></span></div>\n'
            '  </div>\n</footer>\n<!-- /bf -->')

def put_footer(t, new, old_start, old_end):
    """first run: swap the page's old footer for the shared one; later runs: refresh it"""
    if "<!-- bf -->" in t:
        i = t.index("<!-- bf -->"); j = t.index("<!-- /bf -->") + len("<!-- /bf -->")
    else:
        i = t.index(old_start); j = t.index(old_end, i) + len(old_end)
    return t[:i] + new + t[j:]


def cut(t, start, end, new, what):
    """replace from the line starting with `start` up to (not including) the line starting with `end`"""
    i = t.find(start)
    j = t.find(end, i + 1)
    if i < 0 or j < 0:
        sys.exit(f"header.py: could not find {what}")
    return t[:i] + new + t[j:]


def must(t, old, new, what, n=1):
    if t.count(old) != n:
        sys.exit(f"header.py: {what}: expected {n}, found {t.count(old)}")
    return t.replace(old, new)


def rw(name, fn):
    p = os.path.join(ROOT, name)
    raw = open(p, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    t = raw.replace("\r\n", "\n")
    n = fn(t)
    if crlf:
        n = n.replace("\n", "\r\n")
    if n != raw:
        open(p, "w", encoding="utf-8", newline="").write(n)
    print(("updated " if n != raw else "unchanged ") + name)


# ── the case studies page ────────────────────────────────────────────────
MAIN_HEADER = header("#reel",
    mid='<a href="#reel" data-v="reel" class="on">Stories</a><a href="#all" data-v="all">Case studies</a>',
    lang=f'<a class="bh-lang" href="{AR_URL}" lang="ar" hreflang="ar">العربية</a>', tone="clear")

def main_page(t):
    if "/* bh:css */" not in t:  # first run: take out the old header
        glass = t[t.index("/* liquid glass:"):t.index(".lgp{display:flex")]
        t = cut(t, ".nav{position:fixed;z-index:80", ".tabbar{display:none}", f"/* bh:css */\n{CSS}\n/* /bh:css */\n" + glass, "old header CSS")
        t = must(t, "  .views{display:none}\n  .nav .cta{font-size:12.5px;gap:8px;padding:4px 4px 4px 14px}\n  .nav .cta i{width:30px;height:30px}\n", "", "phone header rules")
        i = t.index('<nav class="nav" aria-label="Main">'); j = t.index("</nav>", i) + len("</nav>")
        t = t[:i] + MAIN_HEADER + t[j:]
        # the page drives the header through BH instead of its own copy
        i = t.index("  // nav: black wordmark over light surfaces"); j = t.index("    const lightAt = yy =>", i)
        t = t[:i] + ('  // the header follows the page: clear over the story, tinted by the client once scrolled,\n'
                     '  // light over paper; its live line says where the reader is\n'
                     '  let hbAc = "#262626", hbCase = 0, tickNow = "";\n  const setTick = s => { tickNow = s; BH.tick(s); };\n'
                     '  function navTone() {\n    const s = stage.getBoundingClientRect(), solid = s.bottom < 72, y = scrollY;\n') + t[j:]
        t = must(t, '    // clear glass at the very top reads the stage colour; once scrolled it is smoked glass, light only over paper\n    const light = solid ? lightAt(34) : (y < 8 && stage.classList.contains("lite"));\n'
                    '    n.classList.toggle("solid", solid); n.classList.toggle("light", light); n.classList.toggle("top", y < 8);\n'
                    '    document.documentElement.style.setProperty("--hb", solid ? "#262626" : hbAc);\n',
                 '    BH.tone(solid ? (lightAt(34) ? "light" : "dark") : y < 8 ? (stage.classList.contains("lite") ? "clear-ink" : "clear") : "dark");\n'
                 '    BH.tint(solid ? "#262626" : hbAc);\n', "tone lines")
    else:
        i = t.index("<!-- bh -->"); j = t.index("<!-- /bh -->") + len("<!-- /bh -->")
        t = t[:i] + MAIN_HEADER + t[j:]
    return sync(t)

rw("case-studies.html", main_page)


# ── the case pages (rendered by the case engine) ─────────────────────────
ENGINE_HEADER = ('      <header class="bh" id="bh" data-tone="${bhTop}"><div class="bh-bar">\n'
    '        <div class="bh-start"><a class="bh-logo" href="${esc(opts.storiesUrl)}" aria-label="Brandita, home">'
    '${opts.logo ? `<img class="w" src="${opts.logo}" alt="Brandita" width="' + str(WM_W) + '" height="' + str(WM_H) + '">` : ""}'
    '${opts.logoK ? `<img class="k" src="${opts.logoK}" alt="" width="' + str(WM_W) + '" height="' + str(WM_H) + '">` : ""}</a>'
    '<span class="bh-tag">Digital marketing · Cairo</span></div>\n'
    '        <nav class="bh-mid" aria-label="Main"><a href="${esc(opts.storiesUrl)}">Stories</a><a href="${esc(opts.storiesUrl)}#all" aria-current="page">Case studies</a></nav>\n'
    '        <div class="bh-end"><span class="bh-tick" aria-live="polite"><i class="bh-ring" aria-hidden="true"></i><span class="bh-tx">${esc(c.client)}</span></span>'
    '<a class="bh-cta" href="${esc(opts.bookUrl)}" data-cursor="Book"><span>Book a call</span><i aria-hidden="true">${ARROW}</i></a></div>\n'
    '      </div></header>')

def engine_js(t):
    if "/* bh:js */" not in t:
        t = f"/* bh:js */\n{JS}\n/* /bh:js */\n" + t
        i = t.index('      <nav class="cx-nav" aria-label="Case">'); j = t.index("</div></nav>", i) + len("</div></nav>")
        t = t[:i] + ENGINE_HEADER + t[j:]
        # light case grounds take ink type in the header, dark ones bone
        t = must(t, "    root.innerHTML = `\n", "    const bhLite = (n => .299 * (n >> 16) + .587 * (n >> 8 & 255) + .114 * (n & 255) > 150)(parseInt(p.bg.slice(1), 16));\n"
                 "    const bhTop = bhLite ? \"clear-ink\" : \"clear\", bhOn = bhLite ? \"light\" : \"dark\";\n    root.innerHTML = `\n", "render start")
        t = must(t, "    wire(c, R, root, opts, reduced);\n    return {", "    window.BH = window.BH_init(); BH.tint(bhLite ? \"#262626\" : p.accent);\n"
                 "    wire(c, R, root, opts, reduced, bhTop, bhOn);\n    return {", "wire call")
        t = must(t, "  function wire(c, R, root, opts, reduced) {", "  function wire(c, R, root, opts, reduced, bhTop, bhOn) {", "wire signature")
        i = t.index("    // progress bar, chapter index, the hiding nav"); j = t.index("    addEventListener(\"scroll\", () => { if (!ticking)", i)
        t = t[:i] + ('    // progress bar, chapter index; the header (bh) says which chapter is open and how far in the reader is\n'
                     '    const prog = $(".cx-prog i"), ix = $$(".cx-index a"), secs = ix.map(a => $("#" + a.dataset.ix));\n'
                     '    let ticking = false;\n'
                     '    const onScroll = () => { ticking = false; const y = scrollY, h = document.documentElement.scrollHeight - innerHeight;\n'
                     '      prog.style.transform = `scaleX(${h > 0 ? (y / h).toFixed(4) : 0})`;\n'
                     '      let on = -1; secs.forEach((s, k) => { if (s && s.getBoundingClientRect().top < innerHeight * .45) on = k; }); ix.forEach((a, k) => a.classList.toggle("on", k === on));\n'
                     '      BH.tick(on < 0 ? c.client : `${pad(on + 1)} · ${ix[on].textContent}`);\n'
                     '      BH.progress(h > 0 ? y / h : 0); BH.tone(y < 8 ? bhTop : bhOn);\n'
                     '      runUpdate(); };\n') + t[j:]
    return sync(t)

def engine_css(t):
    if "/* bh:css */" not in t:
        i = t.index(".cx-nav{position:fixed"); j = t.index("\n", t.index("@media (max-width:560px){.cx-nav .hb")) + 1
        t = t[:i] + f"/* bh:css */\n{CSS}\n/* /bh:css */\n" + t[j:]
        t = must(t, ".cx.embed .cx-nav,.cx.embed .cx-index{display:none}", ".cx.embed .bh,.cx.embed .cx-index{display:none}", "embed rule")
    return sync(t)

def builder(t):
    if '"logoK"' in t:
        return t
    t = must(t, '"logo": logo_uri,', '"logo": _B["wm_en_white"]["uri"], "logoK": _B["wm_en_black"]["uri"],', "builder opts")
    return t

rw("case-engine/engine.js", engine_js)
rw("case-engine/engine.css", engine_css)
rw("case-engine/build_cases.py", builder)


# ── the two landing pages ────────────────────────────────────────────────
STORES_HEADER = header("#top", tick="dot", attrs={"auto": "page", "spy": ""}, space=True, tone="clear", tag="",
    mid='<a href="#leaks">Where orders leak</a><a href="#calc">Calculator</a><a href="#how">How it works</a><a href="#faq">Questions</a>'
        f'<a href="{EN_URL}">Case studies</a>')

def stores(t):
    if "<!-- bh -->" not in t:
        i = t.index('<nav class="nav" aria-label="Main">'); j = t.index("</nav>", i) + len("</nav>")
        t = t[:i] + STORES_HEADER + t[j:]
        i = t.index("/* ── nav ──"); j = t.index("@media (max-width:760px){.nav .links{display:none}}\n", i) + len("@media (max-width:760px){.nav .links{display:none}}\n")
        t = t[:i] + f"/* bh:css */\n{CSS}\n/* /bh:css */\n" + t[j:]
        t = must(t, '.nav a[href="#top"]{display:inline-flex;padding:11px 4px;margin:-11px -4px}\n', "", "old wordmark tap rule")
    else:
        i = t.index("<!-- bh -->"); j = t.index("<!-- /bh -->") + len("<!-- /bh -->")
        t = t[:i] + STORES_HEADER + t[j:]
    return sync(t)

SWITCH = '<div class="switch"><span>Case study</span><div class="seg" id="seg" role="group" aria-label="Choose client"><span class="thumb" id="thumb"></span></div></div>'
CLIENT_HEADER = header("#top", mid=SWITCH, mid_keep=True, tick=None, attrs={"auto": "page"}, space=True, tone="clear",
    cta_href="https://claude.ai/artifact/Ny51PSz3Cb51nps8m1j7D6#start")

def client(t):
    if "<!-- bh -->" not in t:
        i = t.index('<div class="sample">'); k = t.index("</div></div>", i) + len("</div></div>")
        sample = t[i:k]
        j = t.index("</nav>", k) + len("</nav>")
        t = t[:i] + CLIENT_HEADER + "\n" + sample + t[j:]
        i = t.index(".nav{position:sticky"); j = t.index(".switch{display:flex", i)
        t = t[:i] + f"/* bh:css */\n{CSS}\n/* /bh:css */\n" + t[j:]
        t = must(t, '.nav .cta{font-size:13.5px;font-weight:700;padding:9px 16px;border-radius:999px;background:var(--fg);color:var(--paper);text-decoration:none;white-space:nowrap}\n', "", "old cta")
        t = must(t, "@media (max-width:760px){.switch>span:first-child,.nav .cta{display:none}}", "@media (max-width:760px){.switch>span:first-child{display:none}}", "phone switch rule")
        t = must(t, "@media (max-width:400px){.seg button{padding:6px 9px;font-size:12px}.wm{height:17px}.nav .wrap{gap:8px}}", "@media (max-width:400px){.seg button{padding:6px 9px;font-size:12px}}", "small phone rule")
    else:
        i = t.index("<!-- bh -->"); j = t.index("<!-- /bh -->") + len("<!-- /bh -->")
        t = t[:i] + CLIENT_HEADER + t[j:]
    return sync(t)

rw("ecommerce-landing.html", stores)
rw("client-case.html", client)


# ── footers ──────────────────────────────────────────────────────────────
def drop_lines(t, starts):
    return "\n".join(l for l in t.split("\n") if not l.strip().startswith(starts))

def main_footer(t):
    t = put_footer(t, footer("#reel", "#all", "#start", top="#reel", lang=f'<a href="{AR_URL}" lang="ar" hreflang="ar">العربية</a>'),
                   '<footer class="site-foot">', "</footer>")
    return sync(drop_lines(t, (".site-foot",)))

def landing_footer(book):
    def fn(t):
        new = footer(EN_URL, EN_URL + "#all", book)
        if "<!-- bf -->" in t:
            return sync(put_footer(t, new, "", ""))
        # the old promo cards, industry links and footer close the last section; the shared footer follows it
        i = t.index('    <nav class="family"'); j = t.index("</footer>", i) + len("</footer>\n")
        t = t[:i] + t[j:]
        k = t.index("</section>", i) + len("</section>")
        t = t[:k] + "\n" + new + t[k:]
        return sync(drop_lines(t, (".family", ".inds", "footer{", "footer img")))
    return fn

ENGINE_FOOTER = footer("${esc(opts.storiesUrl)}", "${esc(opts.storiesUrl)}#all", "${esc(opts.bookUrl)}", top="#case")

def engine_footer(t):
    if "<!-- bf -->" not in t:
        t = must(t, "${end(c, opts)}\n", "${end(c, opts)}\n      ${opts.embed ? \"\" : `" + ENGINE_FOOTER + "`}\n", "engine end")
    else:
        i = t.index("<!-- bf -->"); j = t.index("<!-- /bf -->") + len("<!-- /bf -->")
        t = t[:i] + ENGINE_FOOTER + t[j:]
    return t

rw("case-studies.html", main_footer)
rw("ecommerce-landing.html", landing_footer("#start"))
rw("client-case.html", landing_footer(STORES_URL + "#start"))
rw("case-engine/engine.js", engine_footer)
rw("case-engine/engine.css", sync)
