/* Brandita header (bh) behaviour — synced into each page by header.py.
   BH.tone("clear" | "clear-ink" | "dark" | "light"), BH.tint(hex), BH.tick(text),
   BH.progress(0..1). Hides on a real scroll down, returns the moment the reader
   turns back; phone toolbar resizes are never read as scrolling. */
window.BH_init = function () {
  var el = document.getElementById("bh"); if (!el) return { tone: function () {}, tint: function () {}, tick: function () {}, progress: function () {} };
  var tx = el.querySelector(".bh-tx"), ring = el.querySelector(".bh-ring"), now = tx ? tx.textContent : "";
  var reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var lastY = scrollY, run = 0, hold = 0, ticking = false;
  var holdNav = function () { hold = performance.now() + 450; lastY = scrollY; run = 0; };
  addEventListener("resize", holdNav, { passive: true });
  if (window.visualViewport) visualViewport.addEventListener("resize", holdNav, { passive: true });
  function onScroll() {
    ticking = false; var y = scrollY, dy = y - lastY; lastY = y; if (!dy) return;
    if (y < innerHeight * .6 || el.contains(document.activeElement)) { run = 0; el.classList.remove("is-hidden"); return; }
    if (performance.now() < hold) return;
    run = (dy > 0) === (run > 0) ? run + dy : dy;
    if (run < -6) el.classList.remove("is-hidden"); else if (run > 36) el.classList.add("is-hidden");
  }
  addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  el.addEventListener("focusin", function () { el.classList.remove("is-hidden"); });
  // optional, for pages without their own header logic:
  // data-auto="dark" → clear at the very top, that tone once scrolled;
  // data-spy → the centre link of the section on screen is marked current, and named in the live line
  var auto = el.getAttribute("data-auto"), spy = el.hasAttribute("data-spy") ? [].slice.call(el.querySelectorAll('.bh-mid a[href^="#"]')) : [];
  function follow() {
    if (auto) {
      var t = auto;
      if (auto === "page") { // follow the page's own light or dark scheme
        var bg = getComputedStyle(document.body).backgroundColor;
        if (/rgba\(.*,\s*0\)$/.test(bg) || bg === "transparent") bg = getComputedStyle(document.documentElement).backgroundColor;
        var c = (bg.match(/\d+/g) || [0, 0, 0]).map(Number);
        t = .299 * c[0] + .587 * c[1] + .114 * c[2] > 150 ? "light" : "dark";
      }
      el.dataset.tone = scrollY < 8 ? (t === "light" ? "clear-ink" : "clear") : t;
    }
    var cur = null;
    spy.forEach(function (a) { var s = document.getElementById(a.getAttribute("href").slice(1)); if (s && s.getBoundingClientRect().top < innerHeight * .4) cur = a; });
    spy.forEach(function (a) { if (a === cur) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current"); });
    if (spy.length && api) api.tick(cur ? cur.textContent : "");
  }
  if (auto || spy.length) { addEventListener("scroll", follow, { passive: true }); setTimeout(follow, 0); }
  var api = {
    tone: function (t) { if (el.dataset.tone !== t) el.dataset.tone = t; },
    tint: function (hex) { el.style.setProperty("--bh-tint", hex || "#262626"); },
    progress: function (p) { if (ring) ring.style.setProperty("--p", Math.max(0, Math.min(1, p)).toFixed(3)); },
    tick: function (s) {
      if (!tx || !s || s === now) return; now = s;
      if (reduced || !tx.textContent) { tx.textContent = s; return; }
      tx.classList.add("out");
      setTimeout(function () { tx.textContent = s; tx.classList.remove("out"); tx.classList.add("in"); void tx.offsetWidth; tx.classList.remove("in"); }, 240);
    }
  };
  return api;
};
window.BH = window.BH_init();
