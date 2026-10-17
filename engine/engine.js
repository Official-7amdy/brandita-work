/* Brandita case engine.
   render(caseFile, root, opts) reads a case file, works out what it can say,
   and composes a story from the chapters its data supports. It never adds a
   figure the file does not hold: derived numbers (multiples, ratios, margins)
   are computed from the file and labelled "computed from the case file". */
(function (global) {
  "use strict";
  const esc = s => String(s == null ? "" : s).replace(/[&<>"]/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
  const n0 = v => Math.round(v).toLocaleString("en-US");
  const pad = n => String(n).padStart(2, "0");
  const money = (v, cur) => (cur || "EGP") + " " + (v >= 1e6 ? (v / 1e6).toFixed(2) + "M" : v >= 1e4 ? Math.round(v / 1e3) + "K" : n0(v));
  const x1 = v => (Math.round(v * 10) / 10).toFixed(1) + "×";
  const ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>';
  const CAL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>';

  /* ══ read: what the case file can support, and what follows from it ══ */
  function read(c) {
    const R = {};
    const s = c.series;
    if (s && s.rows && s.rows.length > 2) {
      const rows = s.rows, first = rows[0];
      const argmax = k => rows.reduce((b, r, i) => (r[k] > rows[b][k] ? i : b), 0);
      const peakI = argmax("sales"), spendI = argmax("spend");
      const mom = rows.map((r, i) => (i ? (r.orders / rows[i - 1].orders - 1) * 100 : 0));
      let dipI = -1; // the deepest fall, leaving out the sheet's last month (it may be partial)
      mom.forEach((m, i) => { if (i > 0 && i < rows.length - 1 && m < 0 && (dipI < 0 || m < mom[dipI])) dipI = i; });
      const roas = rows.map(r => r.roas);
      R.series = { peakI, spendI, dipI, mom, spendX: rows[spendI].spend / first.spend, salesX: rows[peakI].sales / first.sales,
        roasMin: Math.min(...roas), roasMax: Math.max(...roas), cppPeak: (rows[peakI].cpp / first.cpp - 1) * 100 };
    }
    if (c.hooks && c.hooks.rows) {
      const rows = c.hooks.rows, still = rows.filter(r => r.static), moving = rows.filter(r => !r.static);
      const avg = a => a.reduce((t, r) => t + r.rate, 0) / a.length;
      if (still.length && moving.length) R.hooks = { moving: avg(moving), still: avg(still), ratio: avg(moving) / avg(still) };
    }
    if (c.levers) R.levers = { won: c.levers.filter(l => l.status === "won").length, miss: c.levers.filter(l => l.status === "miss").length };
    if (c.quarters && c.quarters.length > 1) {
      const q = c.quarters, m = q.map(x => (x.profit / x.sales) * 100);
      R.quarters = { growth: q[q.length - 1].sales / q[0].sales, margins: m, flat: Math.max(...m) - Math.min(...m) < 1 };
    }
    return R;
  }

  /* ══ plan: chapters in story order, only where the file has the material ══ */
  function plan(c, R) {
    const ch = [["brief", "The brief"]];
    if (c.before || c.leak) ch.push(["before", "Before"]);
    if (R.series) ch.push(["run", "The run"]);
    if (c.levers || c.steps) ch.push(["work", "The work"]);
    if (R.hooks) ch.push(["creative", "The creative"]);
    if (c.store || c.adAccount || (c.evidence && c.evidence.length)) ch.push(["evidence", "The evidence"]);
    if (c.outcomes || c.quarters || c.compare || c.totals) ch.push(["result", "The result"]);
    if (c.misses || c.miss) ch.push(["miss", "What did not work"]);
    return ch;
  }

  // the cover's proof points: computed from the series when there is one, else the headline metric
  function proof(c, R) {
    const S = R.series, s = c.series;
    if (!S) return [[c.metric.value, c.metric.label]];
    return [[x1(S.spendX), `monthly ad spend, ${s.months[0]} to ${s.months[S.spendI]}`], [x1(S.salesX), `monthly sales, ${s.months[0]} to ${s.months[S.peakI]}`],
      [`${S.roasMin.toFixed(2)}–${S.roasMax.toFixed(2)}×`, `ROAS, every month of ${s.year}`]];
  }
  const head = (i, kicker, title) => `<header class="cx-h rv"><span class="cx-n" aria-hidden="true">${pad(i)}</span><div><span class="cx-k">${esc(kicker)}</span><h2 class="cx-t">${title}</h2></div></header>`;
  const accent = (text, word) => { const t = esc(text), w = esc(word); return w && t.includes(w) ? t.replace(w, `<em>${w}</em>`) : t; };

  /* ══ chapters ══ */
  const B = {
    cover(c, R) {
      return `<header class="cx-cover" id="top">
        <div class="cx-cover-bg" aria-hidden="true">${esc(c.metric.value)}</div>
        <div class="cx-wrap">
          <div class="cx-tags rv">${c.real ? '<span class="tag real">Real client</span>' : '<span class="tag smp">Sample file</span>'}<span class="tag">${esc(c.line)}</span><span class="tag">${esc(c.sector)}</span></div>
          <p class="cx-client rv d1">${esc(c.fullName || c.client)}${c.period ? " · " + esc(c.period) : ""}</p>
          <h1 class="cx-title rv d1">${accent(c.headline, c.metric.value)}</h1>
          <div class="cx-proof rv d2">${proof(c, R).map(([v, l]) => `<div><b class="tnum" data-count="${esc(v)}">${esc(v)}</b><span>${esc(l)}</span></div>`).join("")}</div>
          ${c.real ? "" : '<p class="cx-src rv d3">Sample file. The client and every figure are placeholders that show the format a real case follows.</p>'}
        </div></header>`;
    },
    brief(c, R, i) {
      const cells = c.real
        ? [["Client", c.fullName || c.client], ["Industry", c.sector + (c.market ? ", " + c.market : "")], ["Services", (c.services || [c.line]).join(", ")], ["Period", c.period], ["Result", c.metric.value]]
        : [["Sector", c.sector], ["Service line", c.line], ["Result", c.metric.value], ["Measured as", c.metric.label], ["Status", "Sample, placeholder figures"]];
      return `<section class="cx-ch" id="brief"><div class="cx-wrap">${head(i, "The brief", c.real ? "One brand, one account, <em>one number.</em>" : "The format, with <em>sample</em> figures.")}
        ${c.summary ? `<p class="cx-sum rv">${esc(c.summary)}</p>` : ""}
        <dl class="cx-brief rv">${cells.map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join("")}</dl></div></section>`;
    },
    before(c, R, i) {
      if (c.before) return `<section class="cx-ch" id="before"><div class="cx-wrap">${head(i, "Before", accent(c.before.title, "ads."))}
        <div class="cx-wall rv">${c.before.constraints.map(t => `<span>${esc(t)}</span>`).join("")}</div>
        <span class="cx-k rv">What the audit found</span>
        <ol class="cx-audit rv" style="margin-top:18px">${c.before.audit.map(t => `<li>${esc(t)}</li>`).join("")}</ol></div></section>`;
      return `<section class="cx-ch" id="before"><div class="cx-wrap">${head(i, "The leak", "Where the orders were <em>going.</em>")}
        <p class="cx-quote rv">${esc(c.leak)}</p><p class="cx-lede rv">${esc(c.sub || "")}</p></div></section>`;
    },
    run(c, R, i) {
      const s = c.series, rows = s.rows, mx = Math.max(...rows.map(r => r.sales)), S = R.series;
      return `<section class="cx-ch" id="run"><div class="cx-wrap">${head(i, "The run", `Spend up ${x1(S.spendX)}. Return held <em>the whole way.</em>`)}
        <p class="cx-lede rv">Scroll through the year, month by month, from ${esc(s.source)}.</p></div>
        <div class="run" style="--n:${rows.length}"><div class="run-sticky cx-wrap">
          <div class="run-l"><span class="run-mo" data-r="mo"></span><b class="run-big tnum" data-r="big"></b><small>sales that month</small>
            <dl class="run-stats"><div><dt>Ad spend</dt><dd class="tnum" data-r="spend"></dd></div><div><dt>ROAS</dt><dd class="tnum hot" data-r="roas"></dd></div>
              <div><dt>Orders</dt><dd class="tnum" data-r="orders"></dd></div><div><dt>Cost per purchase</dt><dd class="tnum" data-r="cpp"></dd></div></dl>
            <p class="run-note" data-r="note"></p></div>
          <div><div class="run-chart" role="img" aria-label="Monthly ad spend and sales, ${esc(s.months[0])} to ${esc(s.months[s.months.length - 1])} ${esc(s.year)}">
            ${rows.map((r, k) => `<div class="run-col" data-k="${k}"><i class="sp" style="--h:${(r.spend / mx).toFixed(4)}"></i><i class="sa" style="--h:${(r.sales / mx).toFixed(4)}"></i><span>${esc(s.months[k])}</span></div>`).join("")}</div>
            <div class="run-key"><span><i style="background:var(--rule)"></i>Ad spend</span><span><i style="background:var(--ac)"></i>Sales</span></div></div>
        </div></div>
        <div class="cx-wrap"><div class="cx-insight rv"><b class="tnum">${x1(S.salesX)}</b><p>${esc(s.monthsLong[S.peakI])} sales against ${esc(s.monthsLong[0])}, while ROAS stayed between ${S.roasMin.toFixed(2)}× and ${S.roasMax.toFixed(2)}× every month.<small>Computed from the case file.</small></p></div>${srcCards(c, "run", "The sheet these months come from")}</div></section>`;
    },
    work(c, R, i) {
      if (c.levers) return `<section class="cx-ch" id="work"><div class="cx-wrap">${head(i, "The work", `${c.levers.length} levers. Every one <em>tested.</em>`)}
        <p class="cx-lede rv" style="margin-bottom:28px">${R.levers.won} won, ${R.levers.miss} did not. Tap a card for what happened.</p>
        <div class="cx-levers">${c.levers.map((l, k) => `<button data-cursor="Flip" class="lev rv ${l.status === "miss" ? "miss" : ""}" type="button" aria-expanded="false" aria-label="${esc(l.title)}: ${esc(l.stat)}">
          <span class="lev-in"><span class="lev-f"><span class="no" aria-hidden="true">${pad(k + 1)}</span>${l.status ? `<span class="won">${l.status === "won" ? "Worked" : "Did not work"}</span>` : ""}<h3>${esc(l.title)}</h3><span class="st">${esc(l.stat)}</span><span class="tap" aria-hidden="true">Tap to read</span></span>
          <span class="lev-b"><p>${esc(l.detail)}</p></span></span></button>`).join("")}</div></div></section>`;
      return `<section class="cx-ch" id="work"><div class="cx-wrap">${head(i, "The work", "Four stages, each with a <em>document.</em>")}
        <ol class="cx-steps cx-steps-wrap">${c.steps.map(([t, d], k) => `<li class="rv d${k % 4}"><span class="no">${pad(k + 1)}</span><b>${esc(t)}</b><span>${esc(d)}</span></li>`).join("")}</ol></div></section>`;
    },
    creative(c, R, i) {
      const H = c.hooks, top = Math.max(...H.rows.map(r => r.rate));
      return `<section class="cx-ch" id="creative"><div class="cx-wrap">${head(i, "The creative", "Stories pulled people in. Hard selling <em>did not.</em>")}
        <div class="cx-insight rv" style="margin:0 0 30px"><b class="tnum">${Math.round(R.hooks.ratio)}×</b><p>more viewers held by story and curiosity videos (${R.hooks.moving.toFixed(1)}% average hook rate) than by hard-selling statics (${R.hooks.still.toFixed(2)}%).<small>Computed from the case file. ${esc(H.note)}</small></p></div>
        <div class="reel" data-cursor="Drag">${H.rows.map(r => `<article class="ph ${r.static ? "still" : ""}"><div class="bar"><b></b></div><span class="dir">${esc(r.direction)}</span>
          <p class="ar" lang="ar" dir="rtl">${esc(r.text)}</p><p class="en">${esc(r.en)} <i>(translated)</i></p><p class="vis">${esc(r.visual)}</p>
          <div class="meter"><span><i style="--w:${Math.max(.01, r.rate / top).toFixed(3)}"></i></span><b class="tnum">${r.rate.toFixed(2)}%</b></div></article>`).join("")}</div>
        <p class="cx-src">Executions are illustrated from the real hooks; the hook rates are measured.</p>${feed(c)}${srcCards(c, "creative", "How the creative was made")}</div></section>`;
    },
    evidence(c, R, i) {
      const tabs = [];
      if (c.store && c.series) tabs.push(["store", "Store dashboard"]);
      if (c.adAccount) tabs.push(["ads", "Ad account"]);
      if (c.evidence && c.evidence.length) tabs.push(["shots", "Screenshots"]);
      return `<section class="cx-ch" id="evidence"><div class="cx-wrap">${head(i, "The evidence", "Opened straight from the <em>accounts.</em>")}
        <p class="cx-lede rv" style="margin-bottom:26px">The numbers above, in the places they came from. The dashboard and the ad ledger are rebuilt from the exports so you can explore them; the screenshots are the originals, with names and IDs hidden.</p>
        <div class="ev-tabs rv" role="tablist">${tabs.map(([k, t], j) => `<button type="button" role="tab" id="tab-${k}" aria-controls="ev-${k}" aria-selected="${j === 0}">${t}</button>`).join("")}</div>
        ${tabs.map(([k], j) => `<div class="ev-panel" role="tabpanel" id="ev-${k}" aria-labelledby="tab-${k}"${j ? " hidden" : ""}>${k === "store" ? store(c) : k === "ads" ? ledger(c) : wall(c)}</div>`).join("")}
      </div></section>`;
    },
    result(c, R, i) {
      let h = `<section class="cx-ch" id="result"><div class="cx-wrap">`;
      if (c.real) {
        h += head(i, "The result", "More sales every quarter, at the same <em>margin.</em>");
        if (c.outcomes) h += `<div class="cx-ba rv">${c.outcomes.map(o => `<div><span class="k">${esc(o.label)}</span><span class="from">From <s>${esc(o.from)}</s></span><span class="to tnum${o.hot ? " hot" : ""}">${esc(o.to)}</span><span class="when">${esc(o.when)}</span></div>`).join("")}</div>`;
        if (c.quarters) {
          const mx = Math.max(...c.quarters.map(q => q.sales)) * 1.02, m = R.quarters.margins, avg = m.reduce((a, b) => a + b, 0) / m.length;
          h += `<div class="cx-q rv"><div>${c.quarters.map((q, k) => `<div class="qrow"><div class="top"><span>${esc(q.q)} · ${money(q.sales)} sales</span><span class="tnum">${money(q.profit)} net profit · ${m[k].toFixed(1)}%</span></div>
            <div class="tr"><i style="--w:${(q.sales / mx).toFixed(3)}"></i><i class="p" style="--w:${(q.profit / mx).toFixed(3)}"></i></div></div>`).join("")}
            <p class="cx-src">${esc(c.quartersSource || "")}</p></div>
            <div><div class="ring" style="--p:${(avg / 100).toFixed(3)}"><b class="tnum">${Math.round(avg)}%<small>net profit / sales${R.quarters.flat ? ", every quarter" : ""}</small></b></div>
            <p class="cx-src" style="text-align:center">Sales grew ${x1(R.quarters.growth)} from ${esc(c.quarters[0].q)} to ${esc(c.quarters[c.quarters.length - 1].q)}. Computed from the case file.</p></div></div>`;
        }
        if (c.totals) h += `<div class="cx-tot rv">${c.totals.map(t => `<div><b class="tnum">${esc(t.value)}</b><span>${esc(t.label)}</span></div>`).join("")}</div><p class="cx-src">${esc(c.totalsSource || "")}</p>${srcCards(c, "result", "From Lazoomi's own books")}`;
      } else {
        h += head(i, "The result", "Same reporting source, before and <em>after.</em>");
        h += `<div class="cx-big tnum rv" data-count="${esc(c.metric.value)}">${esc(c.metric.value)}</div><p class="cx-lede rv" style="margin-bottom:36px">${esc(c.metric.label)}</p>
          <div class="cx-cmp rv">${c.compare.map(([nm, b, bl, a, al, mx]) => `<div><span class="nm">${esc(nm)}</span>
            <div class="r"><span>Before</span><span class="tr"><i style="--w:${(b / mx).toFixed(3)}"></i></span><b class="tnum">${esc(bl)}</b></div>
            <div class="r af"><span>After</span><span class="tr"><i style="--w:${(a / mx).toFixed(3)}"></i></span><b class="tnum">${esc(al)}</b></div></div>`).join("")}</div>
          <p class="cx-src">Sample file with placeholder figures. It shows the format a real case follows.</p>`;
      }
      return h + `</div></section>`;
    },
    miss(c, R, i) {
      const items = c.misses || [{ kind: "Did not work", title: c.miss, detail: "" }];
      return `<section class="cx-ch" id="miss"><div class="cx-wrap">${head(i, "What did not work", "We publish the <em>misses.</em>")}
        <div class="cx-miss ${items.length === 1 ? "one" : ""}">${items.map((m, k) => `<article class="rv d${k}"><span class="cx-k">${esc(m.kind)}</span><b>${esc(m.title)}</b>${m.detail ? `<p>${esc(m.detail)}</p>` : ""}</article>`).join("")}</div>
        <p class="cx-src">They are how the next test gets chosen.</p></div></section>`;
    }
  };

  /* the store dashboard: an analytics admin rebuilt from the store's export (KPIs)
     and the monthly operations sheet (charts, table). Layout follows the store
     platform's admin; no platform logo, and labelled as rebuilt. */
  const IC = {
    Home: "M4 11.5 12 5l8 6.5V19a1 1 0 0 1-1 1h-4.5v-5h-5v5H5a1 1 0 0 1-1-1z", Orders: "M4 6h16v12H4zM4 13h4l1.5 2h5L16 13h4",
    Products: "M12.6 3.6 20 11a1.4 1.4 0 0 1 0 2l-7 7a1.4 1.4 0 0 1-2 0L3.6 12.6A2 2 0 0 1 3 11.2V5a2 2 0 0 1 2-2h6.2a2 2 0 0 1 1.4.6zM7.5 7.5h.01",
    Customers: "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4.5 20a7.5 7.5 0 0 1 15 0", Content: "M6 3h8l4 4v14H6zM14 3v4h4M9 12h6M9 16h6",
    Analytics: "M5 20V11M10 20V5M15 20v-6M20 20V9", Marketing: "M4 10v4h3l6 4V6L7 10zM17 9.5a3.5 3.5 0 0 1 0 5", Discounts: "M8 16 16 8M8.5 8.5h.01M15.5 15.5h.01M12 3l2.2 2.2H17v2.8L19.2 10 17 12.2V15h-2.8L12 17.2 9.8 15H7v-2.8L4.8 10 7 7.8V5h2.8z" };
  const SV = d => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${d}"/></svg>`;
  function store(c) {
    const s = c.store, ser = c.series, o = original(c, "store"), ini = s.name.split(/\s+/).map(w => w[0]).join("").slice(0, 2).toUpperCase();
    const spark = { "Total sales": "sales", "Orders": "orders" };
    const chart = (key, label, extra) => `<div class="sx-chart ${extra || ""}" data-chart="${key}" role="img" aria-label="${esc(label)}, ${esc(ser.months[0])} to ${esc(ser.months[ser.months.length - 1])} ${ser.year}">
      <div class="sx-y"></div><svg viewBox="0 0 600 200" preserveAspectRatio="none" aria-hidden="true"><g class="gr"></g><path class="ar"/><path class="ln"/></svg>
      <i class="sx-cross"></i><i class="sx-dot"></i><div class="sx-x"></div><div class="sx-tip" role="status"></div></div>`;
    return `<div class="win sx" data-sd><div class="sx-strip"><span>${esc(s.title)} · rebuilt from the store's ${esc(s.platform || "")} analytics</span>${o ? o.tg : ""}</div>
      <div class="sx-app" data-pane="live">
        <div class="sx-top"><span class="sx-mk" aria-hidden="true">${esc(ini[0])}</span><span class="sx-search">${SV("M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14zM20 20l-4-4")}<span>Search</span><kbd>Ctrl K</kbd></span>
          <span class="sx-me"><i>${esc(ini)}</i><span>${esc(s.name)}</span></span></div>
        <div class="sx-frame">
          <nav class="sx-nav" aria-label="Store admin (rebuilt, not interactive)">${Object.keys(IC).map(k => `<span class="${k === "Analytics" ? "on" : ""}">${SV(IC[k])}${k}</span>`).join("")}</nav>
          <div class="sx-main">
            <div class="sx-h"><b>Analytics</b><span class="sx-chip">${CAL}${esc(s.period)}</span><span class="sx-chip ghost">Compared to the previous period</span></div>
            <div class="sx-kpis">${s.kpis.map(k => `<div class="sx-kpi"><span class="sx-kl">${esc(k.label)}</span><b class="tnum" data-count="${esc(k.value)}">${esc(k.value)}</b>
              ${k.delta ? `<span class="sx-up">${SV("M7 17 17 7M9 7h8v8")}${esc(k.delta.replace("+", ""))}</span>` : ""}
              ${spark[k.label] ? `<svg class="sx-spark" viewBox="0 0 100 30" preserveAspectRatio="none" data-spark="${spark[k.label]}" aria-hidden="true"><path/></svg>` : ""}</div>`).join("")}</div>
            <div class="sx-bar"><span>Charts: monthly, from the operations sheet</span>
              <div class="sx-pick"><button class="sx-btn" type="button" aria-haspopup="true" aria-expanded="false">${CAL}<span data-sx="range">${esc(ser.months[0])}–${esc(ser.months[ser.months.length - 1])} ${ser.year}</span>${SV("M7 10l5 5 5-5")}</button>
                <div class="sx-menu" role="menu" hidden>${[["all", `${ser.months[0]}–${ser.months[ser.months.length - 1]} ${ser.year}`], ["q2", `Q2 ${ser.year}`], ["q3", `Q3 ${ser.year}`], ["q4", `Q4 ${ser.year}`]].map(([k, t]) => `<button type="button" role="menuitemradio" data-q="${k}" aria-checked="${k === "all"}">${t}</button>`).join("")}</div></div></div>
            <div class="sx-grid">
              <section class="sx-card sx-wide"><header><span class="sx-ct">Total sales over time</span>
                <div class="sx-seg" role="group" aria-label="Metric">${[["sales", "Total sales"], ["orders", "Orders"], ["aov", "Average order value"]].map(([k, t], j) => `<button type="button" data-m="${k}" aria-pressed="${j === 0}">${t}</button>`).join("")}</div></header>
                <b class="sx-big tnum" data-sx="main"></b>${chart("main", "Monthly total")}</section>
              <section class="sx-card"><header><span class="sx-ct">Average order value over time</span></header><b class="sx-big sm tnum" data-sx="aov"></b>${chart("aov", "Average order value", "sm")}</section>
              <section class="sx-card"><header><span class="sx-ct">Orders over time</span></header><b class="sx-big sm tnum" data-sx="orders"></b>${chart("orders", "Orders", "sm")}</section>
              <section class="sx-card sx-wide"><header><span class="sx-ct">Sales by month</span></header><div class="sx-tw"><table class="sx-t" data-sxt><thead><tr>
                ${[["k", "Month"], ["orders", "Orders"], ["sales", "Total sales"], ["aov", "Average order value"], ["mom", "Orders vs. prior month"]].map(([k, t]) => `<th scope="col"><button type="button" data-k="${k}">${t}</button></th>`).join("")}</tr></thead><tbody></tbody></table></div></section>
            </div>
            <p class="sx-src">${esc(s.source)}</p>
          </div></div></div>${o ? o.pane : ""}</div>`;
  }
  function ledger(c) {
    const a = c.adAccount, cols = [["name", "Campaign"], ["spend", "Amount spent"], ["purchases", "Purchases"], ["cpp", "Cost / purchase"], ["value", "Purchase value"], ["roas", "ROAS"], ["cvr", "CVR"], ["hook", "Hook rate"], ["start", "Started"]];
    const o = original(c, "ads");
    return `<div class="win"><div class="win-bar"><i></i><i></i><i></i><span>${esc(a.title)} · ${esc(c.client)} · ${a.campaigns} campaigns</span>${o ? o.tg : ""}</div><div class="win-body" data-pane="live">
      <div class="ld-ctl"><span class="sd-range">${CAL}${esc(a.period)}</span><div class="seg" data-ldf><button type="button" data-f="all" aria-pressed="true">All</button><button type="button" data-f="on" aria-pressed="false">Active</button></div></div>
      <div class="ld-scroll"><table class="ld" data-ld><thead><tr>${cols.map(([k, t]) => `<th scope="col"><button type="button" data-k="${k}">${t}</button></th>`).join("")}</tr></thead><tbody></tbody>
        <tfoot><tr><td>All ${a.campaigns} campaigns</td><td>${money(a.totals.spend)}</td><td>${n0(a.totals.purchases)}</td><td>EGP ${a.totals.cpp.toFixed(2)}</td><td>${money(a.totals.value)}</td><td>${a.totals.roas.toFixed(2)}</td><td>${a.totals.cvr.toFixed(2)}%</td><td>${a.totals.hook.toFixed(2)}%</td><td></td></tr></tfoot></table></div>
      <p class="win-src">${esc(a.note)}</p></div>${o ? o.pane : ""}</div>`;
  }
  // evidence placed in the chapter it supports ("place" in the case file)
  const byPlace = (c, p) => (c.evidence || []).map((e, k) => [e, k]).filter(([e]) => e.place === p);
  function srcCards(c, p, label) {
    const items = byPlace(c, p).filter(([e]) => e.kind !== "ad"); if (!items.length) return "";
    const rot = [-1.6, 1.3, -.7];
    return `<div class="srcs rv"><span class="cx-k">${esc(label)}</span><div class="srcs-row">${items.map(([e, k], j) => `<button class="src" type="button" data-shot="${k}" data-cursor="Open" style="--r:${rot[j % 3]}deg" aria-label="Open: ${esc(e.title)}">
      <span class="win-bar"><i></i><i></i><i></i><span>${esc(e.title)}</span></span><img src="img/${esc(e.file)}" alt="${esc(e.title)}: ${esc(e.caption)}" loading="lazy">
      <span class="cap">${esc(e.caption)}${e.hide && e.hide.length ? ` · ${e.hide.length} ${e.hide.length > 1 ? "areas" : "area"} hidden` : ""}</span></button>`).join("")}</div></div>`;
  }
  // a real ad, shown the way people saw it: in a phone, in the feed
  function feed(c) {
    const ad = (c.evidence || []).map((e, k) => [e, k]).find(([e]) => e.kind === "ad"); if (!ad) return "";
    const [e, k] = ad;
    return `<div class="feed rv"><div class="feed-l"><button class="phone" type="button" data-shot="${k}" data-cursor="Open" aria-label="Open the ad: ${esc(e.title)}"><span class="notch" aria-hidden="true"></span><img src="img/${esc(e.file)}" alt="${esc(e.title)}: ${esc(e.caption)}" loading="lazy"></button></div>
      <div class="feed-t"><span class="cx-k">${esc(e.title)}</span><p class="feed-cap">${esc(e.caption)}</p><p class="feed-en">“${esc(e.en)}” <i>(translated)</i></p>
        ${(e.notes || []).map(([h, d]) => `<p class="feed-n"><b>${esc(h)}</b> ${esc(d)}</p>`).join("")}</div></div>`;
  }
  // a rebuilt window can flip to the screenshot it was rebuilt from
  function original(c, p) {
    const it = byPlace(c, p)[0]; if (!it) return null; const [e, k] = it;
    return { tg: `<span class="win-tg" role="group" aria-label="View"><button type="button" data-v="live" aria-pressed="true">Rebuilt</button><button type="button" data-v="orig" aria-pressed="false">Original</button></span>`,
      pane: `<div class="win-orig" data-pane="orig" hidden><button class="wo" type="button" data-shot="${k}" data-cursor="Zoom" aria-label="Open the original screenshot"><img src="img/${esc(e.file)}" alt="${esc(e.title)}: ${esc(e.caption)}" loading="lazy"></button>
        <p class="win-src">${esc(e.title)}, ${esc(e.caption)}.${e.hide && e.hide.length ? " Names and IDs hidden." : ""}</p></div>` };
  }
  function wall(c) {
    const rot = [-2.2, 1.6, -1.1, 2.4, -1.8, 1.2];
    return `<div class="wall">${c.evidence.map((e, k) => `<button class="shot" type="button" data-cursor="Open" data-shot="${k}" style="--r:${rot[k % rot.length]}deg" aria-label="Open screenshot: ${esc(e.title)}">
      <div class="win-bar"><i></i><i></i><i></i><span>${esc(e.title)}</span></div><img src="img/${esc(e.file)}" alt="${esc(e.title)}: ${esc(e.caption)}" loading="lazy">
      <figcaption><b>${esc(e.title)}</b>${esc(e.caption)}${e.hide && e.hide.length ? `<span class="hid">${e.hide.length} ${e.hide.length > 1 ? "areas" : "area"} hidden</span>` : ""}</figcaption></button>`).join("")}</div>`;
  }

  function end(c, opts) {
    const wa = "https://wa.me/201099307190?text=" + encodeURIComponent(`Hi Brandita, I read the ${c.real ? c.client : c.sector.toLowerCase() + " sample"} case and want to talk about my store.`);
    const tgt = opts.embed ? ' target="_top"' : "";
    const nx = opts.next, nextCard = nx ? `<div class="cx-wrap"><${opts.embed ? 'button type="button" data-nextcase' : `a href="${esc(nx.href)}"`} class="cx-nc rv" data-cursor="Next" style="--nb:${esc(nx.bg)};--nf:${esc(nx.fg)};--na:${esc(nx.accent)}">
      <span class="cx-k">Next case</span><span class="nc-c">${esc(nx.title)}</span><b class="nc-t">${esc(nx.headline)}</b><span class="nc-m tnum">${esc(nx.metric)}</span><span class="nc-go" aria-hidden="true">Read it →</span></${opts.embed ? "button" : "a"}></div>` : "";
    return `${nextCard}<section class="cx-end"><div class="cx-wrap"><span class="cx-k rv">Your turn</span>
      <h2 class="rv" style="margin-top:20px">Your number<br>is <em>next.</em></h2>
      <div class="row"><a class="book rv" data-cursor="Book" href="${esc(opts.bookUrl)}"${tgt}><span class="t">Book a free call<small>The audit comes first. The proposal comes after.</small></span><span class="ar" aria-hidden="true">${ARROW}</span></a>
        <nav class="cx-links rv" aria-label="More">${opts.next && !opts.embed ? `<a href="${esc(opts.next.href)}">Next case<span>${esc(opts.next.title)} →</span></a>` : ""}
          <a href="${esc(opts.storiesUrl)}"${tgt}>All case stories<span>Back to the stories →</span></a><a href="${wa}" target="_blank" rel="noopener">WhatsApp us<span>+20 109 930 7190 →</span></a></nav></div>
    </div></section>`;
  }

  /* ══ render ══ */
  function render(c, root, opts) {
    opts = Object.assign({ embed: false, bookUrl: "for-stores.html#start", storiesUrl: "case-studies.html", logo: "", next: null }, opts || {});
    const R = read(c), chapters = plan(c, R), p = c.palette;
    const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
    root.className = "cx" + (opts.embed ? " embed" : "");
    root.style.cssText = `--bg:${p.bg};--fg:${p.fg};--ac:${p.accent};--ai:${p.onAccent}`;
    document.documentElement.style.background = p.bg;
    root.innerHTML = `
      <div class="cx-prog" aria-hidden="true"><i></i></div>
      <nav class="cx-nav" aria-label="Case"><div class="hb gl"><a class="lg" href="${esc(opts.storiesUrl)}">${opts.logo ? `<img src="${opts.logo}" alt="Brandita">` : "Brandita"}<span>Case stories</span></a>
        <span class="hb-tick" aria-live="polite"><i class="hb-ring" aria-hidden="true"></i><span class="hb-tx" data-tick>${esc(c.client)}</span></span>
        <a class="bk" href="${esc(opts.bookUrl)}"><span>Book a call</span><i aria-hidden="true">${ARROW}</i></a></div></nav>
      <nav class="cx-index" aria-label="Chapters">${chapters.map(([k, t]) => `<a href="#${k}" data-ix="${k}"><span>${esc(t)}</span><i></i></a>`).join("")}</nav>
      ${B.cover(c, R)}${chapters.map(([k], j) => B[k](c, R, j + 1)).join("")}${end(c, opts)}
      <div class="cx-lb" hidden role="dialog" aria-modal="true" aria-label="Screenshot"><figure><p></p></figure><button type="button" aria-label="Close">×</button></div>`;
    wire(c, R, root, opts, reduced);
    return { read: R, chapters: chapters.map(x => x[0]) };
  }

  /* ══ wire: reveals, the run, the dashboard, the ledger, the wall ══ */
  function wire(c, R, root, opts, reduced) {
    const $ = (s, r) => (r || root).querySelector(s), $$ = (s, r) => [...(r || root).querySelectorAll(s)];
    const parse = v => { const m = String(v).match(/^([^\d]*)(\d[\d.,]*)(.*)$/); return m ? { pre: m[1], num: +m[2].replace(/,/g, ""), dec: (m[2].split(".")[1] || "").length, suf: m[3] } : null; };
    const fmt = (p, v) => p.pre + v.toLocaleString("en-US", { minimumFractionDigits: p.dec, maximumFractionDigits: p.dec }) + p.suf;
    function count(el) {
      const p = parse(el.dataset.count); if (!p || reduced) return; const extra = el.querySelector("em"), tail = extra ? extra.outerHTML : "";
      const t0 = performance.now(), dur = 1400;
      const step = now => { const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 4); el.innerHTML = esc(fmt(p, p.num * e)) + tail; if (k < 1) requestAnimationFrame(step); };
      requestAnimationFrame(step);
    }

    // reveals and count-ups, once each
    const io = "IntersectionObserver" in window ? new IntersectionObserver(es => es.forEach(e => { if (!e.isIntersecting) return; const el = e.target; el.classList.add("in"); io.unobserve(el);
      if (el.dataset.count) count(el); $$("[data-count]", el).forEach(count); }), { rootMargin: "0px 0px -6% 0px" }) : null;
    // the cover is on screen at load: reveal it straight away rather than waiting for an intersection
    $$(".cx-cover .rv").forEach((el, k) => setTimeout(() => { el.classList.add("in"); $$("[data-count]", el).forEach(count); }, 60 + k * 40));
    $$(".rv, .reel, .cx-wall, .cx-cmp, [data-count]").filter(el => !el.closest(".cx-cover")).forEach(el => io ? io.observe(el) : el.classList.add("in"));

    // progress bar, chapter index, the hiding nav
    const prog = $(".cx-prog i"), nav = $(".cx-nav"), ix = $$(".cx-index a"), secs = ix.map(a => $("#" + a.dataset.ix));
    let lastY = scrollY, ticking = false, tickNow = "", navRun = 0, hold = 0;
    // the phone toolbar resizes the viewport on every scroll up; never read that as a scroll down
    const holdNav = () => { hold = performance.now() + 450; lastY = scrollY; navRun = 0; };
    addEventListener("resize", holdNav, { passive: true });
    if (window.visualViewport) visualViewport.addEventListener("resize", holdNav, { passive: true });
    const tickEl = $("[data-tick]"), ring = $(".hb-ring");
    const setTick = s => { if (!tickEl || s === tickNow) return; tickNow = s; if (reduced) { tickEl.textContent = s; return; }
      tickEl.classList.add("out"); setTimeout(() => { tickEl.textContent = s; tickEl.classList.remove("out"); tickEl.classList.add("in"); void tickEl.offsetWidth; tickEl.classList.remove("in"); }, 260); };
    const onScroll = () => { ticking = false; const y = scrollY, h = document.documentElement.scrollHeight - innerHeight;
      prog.style.transform = `scaleX(${h > 0 ? (y / h).toFixed(4) : 0})`;
      const dy = y - lastY; lastY = y;
      if (dy) {
        if (y < innerHeight * .8) { navRun = 0; nav.classList.remove("hide"); }
        else if (performance.now() > hold) { navRun = (dy > 0) === (navRun > 0) ? navRun + dy : dy; if (navRun < -6) nav.classList.remove("hide"); else if (navRun > 36) nav.classList.add("hide"); }
      }
      let on = -1; secs.forEach((s, k) => { if (s && s.getBoundingClientRect().top < innerHeight * .45) on = k; }); ix.forEach((a, k) => a.classList.toggle("on", k === on));
      // the header says which chapter is open, and how far through the case the reader is
      setTick(on < 0 ? c.client : `${pad(on + 1)} · ${ix[on].textContent}`);
      if (ring) ring.style.setProperty("--p", h > 0 ? (y / h).toFixed(3) : 0);
      nav.classList.toggle("top", y < 8);
      runUpdate(); };
    addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });

    // the run: scroll position picks the month
    const run = $(".run"); let runK = -1;
    function runUpdate() {
      if (!run) return;
      const r = run.getBoundingClientRect(), span = r.height - innerHeight, pr = Math.min(1, Math.max(0, -r.top / Math.max(1, span)));
      const s = c.series, S = R.series, n = s.rows.length, f = pr * (n - 1), k = Math.round(f);
      $$(".run-col", run).forEach((col, j) => { const g = j < f ? 1 : j < f + 1 ? Math.max(0, 1 - (j - f)) : 0;
        col.querySelectorAll("i").forEach(b => { b.style.transform = `scaleY(${(reduced ? 1 : g) * parseFloat(b.style.getPropertyValue("--h"))})`; }); col.classList.toggle("now", j === k); });
      if (k === runK) return; runK = k;
      const row = s.rows[k];
      $('[data-r="mo"]', run).textContent = s.monthsLong[k] + " " + s.year;
      $('[data-r="big"]', run).textContent = money(row.sales, s.currency);
      $('[data-r="spend"]', run).textContent = money(row.spend, s.currency);
      $('[data-r="roas"]', run).textContent = row.roas.toFixed(2) + "×";
      $('[data-r="orders"]', run).textContent = n0(row.orders);
      $('[data-r="cpp"]', run).textContent = s.currency + " " + Math.round(row.cpp);
      let note = "";
      if (k === 0) note = "Where it started: the first month of the engagement.";
      else if (k === S.peakI) note = `<b>Peak month.</b> ${x1(row.sales / s.rows[0].sales)} the sales of ${esc(s.monthsLong[0])}, at ${row.roas.toFixed(2)}× ROAS.`;
      else if (k === S.dipI) note = `<b>The dip.</b> Orders ${Math.round(S.mom[k])}% on the month before. It is in What did not work.`;
      else if (k === n - 1) note = `The last month in the sheet.`;
      else note = `Orders ${S.mom[k] >= 0 ? "+" : ""}${Math.round(S.mom[k])}% on ${esc(s.monthsLong[k - 1])}.`;
      $('[data-r="note"]', run).innerHTML = note;
    }
    if (run) runUpdate();

    // levers flip on tap
    $$(".lev").forEach(b => b.addEventListener("click", () => b.setAttribute("aria-expanded", String(b.getAttribute("aria-expanded") !== "true"))));

    // evidence tabs (arrow keys move between them)
    const tabs = $$('.ev-tabs [role="tab"]');
    const pick = t => { tabs.forEach(x => { const on = x === t; x.setAttribute("aria-selected", String(on)); x.tabIndex = on ? 0 : -1; $("#" + x.getAttribute("aria-controls")).hidden = !on; }); };
    tabs.forEach((t, k) => { t.tabIndex = k ? -1 : 0; t.addEventListener("click", () => pick(t));
      t.addEventListener("keydown", e => { if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return; const nx = tabs[(k + (e.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length]; pick(nx); nx.focus(); }); });

    // store dashboard: line charts with a crosshair, a range menu, a metric switch, a sortable table
    const sd = $("[data-sd]");
    if (sd && c.series) {
      const s = c.series, cur = s.currency, Q = { all: [0, s.rows.length - 1], q2: [1, 3], q3: [4, 6], q4: [7, 9] };
      const rows = s.rows.map((r, k) => ({ k, mo: s.monthsLong[k], short: s.months[k], orders: r.orders, sales: r.sales, aov: r.aov, mom: k ? (r.orders / s.rows[k - 1].orders - 1) * 100 : null }));
      const F = { sales: v => cur + " " + n0(v), orders: v => n0(v), aov: v => cur + " " + v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) };
      const short = { sales: v => money(v, cur), orders: v => n0(v), aov: v => cur + " " + Math.round(v) };
      let q = "all", m = "sales";
      const yTicks = mx => { const mag = Math.pow(10, Math.floor(Math.log10(mx))), step = Math.ceil(mx / 2 / mag) * mag; return [0, step, step * 2]; };
      function draw(box, key) {
        const [a, b] = Q[q], sel = rows.slice(a, b + 1), vals = sel.map(r => r[key]), ticks = yTicks(Math.max(...vals)), top = ticks[2], n = vals.length;
        const X = i => n === 1 ? 300 : (i / (n - 1)) * 600, Y = v => 196 - (v / top) * 186;
        const pts = vals.map((v, i) => [X(i), Y(v)]);
        const d = pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" ");
        box.querySelector(".ln").setAttribute("d", d);
        box.querySelector(".ar").setAttribute("d", d + ` L600 196 L0 196 Z`);
        box.querySelector(".gr").innerHTML = ticks.map(t => `<line x1="0" x2="600" y1="${Y(t).toFixed(1)}" y2="${Y(t).toFixed(1)}"/>`).join("");
        box.querySelector(".sx-y").innerHTML = ticks.slice().reverse().map(t => `<span style="top:${(Y(t) / 200 * 100).toFixed(2)}%">${short[key](t)}</span>`).join("");
        box.querySelector(".sx-x").innerHTML = sel.map((r, i) => `<span style="left:${(X(i) / 6).toFixed(2)}%">${r.short}</span>`).join("");
        box._pts = pts; box._sel = sel; box._key = key;
        if (!reduced) { const ln = box.querySelector(".ln"), L = ln.getTotalLength ? ln.getTotalLength() : 0;
          if (L) { ln.style.transition = "none"; ln.style.strokeDasharray = L; ln.style.strokeDashoffset = L; ln.getBoundingClientRect(); ln.style.transition = "stroke-dashoffset 1.1s cubic-bezier(.23,1,.32,1)"; ln.style.strokeDashoffset = 0; } }
      }
      const sum = (key, sel) => key === "aov" ? sel.reduce((t, r) => t + r.sales, 0) / sel.reduce((t, r) => t + r.orders, 0) : sel.reduce((t, r) => t + r[key], 0);
      function all() {
        const [a, b] = Q[q], sel = rows.slice(a, b + 1);
        $$(".sx-chart", sd).forEach(x => x.classList.remove("hov")); // a stale tooltip would show the old value
        draw($('[data-chart="main"]', sd), m); draw($('[data-chart="aov"]', sd), "aov"); draw($('[data-chart="orders"]', sd), "orders");
        $('[data-sx="main"]', sd).textContent = F[m](sum(m, sel)); $('[data-sx="aov"]', sd).textContent = F.aov(sum("aov", sel)); $('[data-sx="orders"]', sd).textContent = F.orders(sum("orders", sel));
        $(".sx-card.sx-wide .sx-ct", sd).textContent = { sales: "Total sales over time", orders: "Orders over time", aov: "Average order value over time" }[m];
      }
      // crosshair + tooltip on every chart
      $$(".sx-chart", sd).forEach(box => {
        const tip = $(".sx-tip", box), cross = $(".sx-cross", box), dot = $(".sx-dot", box);
        const at = e => { const r = box.getBoundingClientRect(), x = Math.min(1, Math.max(0, (e.clientX - r.left) / r.width)) * 600, pts = box._pts;
          let i = 0; pts.forEach((p, j) => { if (Math.abs(p[0] - x) < Math.abs(pts[i][0] - x)) i = j; });
          const [px, py] = pts[i], row = box._sel[i], lx = px / 6, ly = py / 2;
          cross.style.left = lx + "%"; dot.style.left = lx + "%"; dot.style.top = ly + "%"; tip.style.left = Math.min(82, Math.max(18, lx)) + "%";
          tip.innerHTML = `<small>${row.mo} ${s.year}</small><b>${F[box._key](row[box._key])}</b>`; box.classList.add("hov"); };
        box.addEventListener("pointermove", at); box.addEventListener("pointerdown", at); box.addEventListener("pointerleave", () => box.classList.remove("hov"));
      });
      // range menu
      const pick = $(".sx-pick", sd), btn = $(".sx-btn", pick), menu = $(".sx-menu", pick);
      btn.addEventListener("click", () => { const open = menu.hidden; menu.hidden = !open; btn.setAttribute("aria-expanded", String(open)); });
      menu.addEventListener("click", e => { const b = e.target.closest("[data-q]"); if (!b) return; q = b.dataset.q; $$("[data-q]", menu).forEach(x => x.setAttribute("aria-checked", String(x === b)));
        $('[data-sx="range"]', sd).textContent = b.textContent; menu.hidden = true; btn.setAttribute("aria-expanded", "false"); all(); });
      document.addEventListener("click", e => { if (!pick.contains(e.target)) { menu.hidden = true; btn.setAttribute("aria-expanded", "false"); } });
      $$(".sx-seg button", sd).forEach(b => b.addEventListener("click", () => { m = b.dataset.m; $$(".sx-seg button", sd).forEach(x => x.setAttribute("aria-pressed", String(x === b))); all(); }));
      // sparklines on the KPI cards
      $$("[data-spark]", sd).forEach(sv => { const v = s.rows.map(r => r[sv.dataset.spark]), mx = Math.max(...v), mn = Math.min(...v);
        sv.querySelector("path").setAttribute("d", v.map((y, i) => (i ? "L" : "M") + (i / (v.length - 1) * 100).toFixed(1) + " " + (28 - (y - mn) / (mx - mn) * 26).toFixed(1)).join(" ")); });
      // the month table, sortable
      const tb = $("[data-sxt] tbody", sd); let tk = "k", td = 1;
      const tdraw = () => { const r = rows.slice().sort((a, b) => td * ((a[tk] == null ? -1e9 : a[tk]) - (b[tk] == null ? -1e9 : b[tk])));
        tb.innerHTML = r.map(x => `<tr><td>${x.mo} ${s.year}</td><td>${n0(x.orders)}</td><td>${F.sales(x.sales)}</td><td>${F.aov(x.aov)}</td><td class="${x.mom == null ? "" : x.mom < 0 ? "dn" : "upc"}">${x.mom == null ? "—" : (x.mom > 0 ? "+" : "") + x.mom.toFixed(1) + "%"}</td></tr>`).join("");
        $$("[data-sxt] th button", sd).forEach(b => { if (b.dataset.k === tk) b.setAttribute("aria-sort", td < 0 ? "descending" : "ascending"); else b.removeAttribute("aria-sort"); }); };
      $$("[data-sxt] th button", sd).forEach(b => b.addEventListener("click", () => { if (tk === b.dataset.k) td = -td; else { tk = b.dataset.k; td = tk === "k" ? 1 : -1; } tdraw(); }));
      tdraw();
      const sdIo = "IntersectionObserver" in window ? new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { all(); sdIo.disconnect(); } }) : null;
      sdIo ? sdIo.observe(sd) : all();
      $$('[data-v="live"]', sd).forEach(b => b.addEventListener("click", () => requestAnimationFrame(all)));
    }

    // ad ledger: sort by any column, filter active
    const ld = $("[data-ld]");
    if (ld && c.adAccount) {
      const A = c.adAccount; let key = "spend", dir = -1, only = false;
      const cell = (k, r) => r[k] == null ? "—" : k === "name" ? `<span class="dot${r.on ? " on" : ""}"></span>${esc(r.name)}` : k === "spend" || k === "value" ? money(r[k]) : k === "cpp" ? "EGP " + r[k].toFixed(2)
        : k === "roas" ? `<span class="${r.roas >= A.totals.roas ? "roas-hi" : ""}">${r.roas.toFixed(2)}</span>` : k === "cvr" || k === "hook" ? r[k].toFixed(2) + "%" : k === "purchases" ? n0(r[k]) : esc(r[k]);
      const cols = $$("th button", ld).map(b => b.dataset.k);
      const draw = () => {
        const rows = A.rows.filter(r => !only || r.on).slice().sort((a, b) => key === "name" || key === "start" ? dir * String(a[key]).localeCompare(String(b[key])) : dir * ((a[key] || 0) - (b[key] || 0)));
        $("tbody", ld).innerHTML = rows.map(r => `<tr>${cols.map(k => `<td>${cell(k, r)}</td>`).join("")}</tr>`).join("");
        $$("th button", ld).forEach(b => { if (b.dataset.k === key) b.setAttribute("aria-sort", dir < 0 ? "descending" : "ascending"); else b.removeAttribute("aria-sort"); });
      };
      $$("th button", ld).forEach(b => b.addEventListener("click", () => { if (key === b.dataset.k) dir = -dir; else { key = b.dataset.k; dir = key === "name" ? 1 : -1; } draw(); }));
      $$("[data-ldf] button", root).forEach(b => b.addEventListener("click", () => { only = b.dataset.f === "on"; $$("[data-ldf] button", root).forEach(x => x.setAttribute("aria-pressed", String(x === b))); draw(); }));
      draw();
    }

    // rebuilt / original
    $$(".win-tg").forEach(g => g.addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return; const w = g.closest(".win");
      $$("button", g).forEach(x => x.setAttribute("aria-pressed", String(x === b))); $('[data-pane="live"]', w).hidden = b.dataset.v !== "live"; $('[data-pane="orig"]', w).hidden = b.dataset.v !== "orig"; }));

    // the hook reel scrolls by dragging with a mouse, with a little momentum
    $$(".reel").forEach(r => { let d = null;
      r.addEventListener("pointerdown", e => { if (e.pointerType !== "mouse") return; d = { x: e.clientX, s: r.scrollLeft, v: 0, t: performance.now() }; r.classList.add("drag"); });
      addEventListener("pointermove", e => { if (!d) return; const now = performance.now(), nx = d.s - (e.clientX - d.x); d.v = (nx - r.scrollLeft) / Math.max(1, now - d.t); d.t = now; r.scrollLeft = nx; });
      addEventListener("pointerup", () => { if (!d) return; let v = d.v * 16; d = null; r.classList.remove("drag");
        const glide = () => { if (Math.abs(v) < .5 || reduced) return; r.scrollLeft += v; v *= .92; requestAnimationFrame(glide); }; glide(); }); });

    // the cursor: a red dot that grows into a label over things you can act on (fine pointers only)
    if (matchMedia("(hover:hover) and (pointer:fine)").matches && !reduced) {
      const cur = document.createElement("div"); cur.className = "cx-cur"; cur.setAttribute("aria-hidden", "true"); cur.innerHTML = "<span></span>";
      document.body.append(cur); document.documentElement.classList.add("cx-curon");
      const lbl = cur.firstChild; let x = -100, y = -100, tx = -100, ty = -100, big = 0, tb = 0, on = false;
      addEventListener("pointermove", e => { if (e.pointerType !== "mouse") return; tx = e.clientX; ty = e.clientY; if (!on) { on = true; x = tx; y = ty; cur.style.opacity = 1; }
        const t = e.target.closest && e.target.closest("[data-cursor]"), l = t ? t.dataset.cursor : ""; tb = l ? 1 : 0; if (l && lbl.textContent !== l) lbl.textContent = l; }, { passive: true });
      document.addEventListener("pointerleave", () => { on = false; cur.style.opacity = 0; });
      const loop = () => { x += (tx - x) * .28; y += (ty - y) * .28; big += (tb - big) * .2;
        cur.style.transform = `translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,0) scale(${(.12 + big * .88).toFixed(3)})`; lbl.style.opacity = big > .6 ? 1 : 0; requestAnimationFrame(loop); };
      requestAnimationFrame(loop);
    }

    // the next case: inside the stories sheet it asks the page to turn to it
    $$("[data-nextcase]").forEach(b => b.addEventListener("click", () => { try { parent.postMessage({ type: "brandita:next" }, "*"); } catch (_) {} }));

    // screenshots open in a lightbox; tap the image to zoom
    const lb = $(".cx-lb"), lbCap = $("p", lb), lbImg = document.createElement("img"); lbImg.alt = ""; let from = null;
    lbCap.before(lbImg); // created here so the page never ships an image without a source
    const close = () => { if (lb.hidden) return; lb.hidden = true; lbImg.classList.remove("zoom"); from && from.focus(); };
    $$("[data-shot]").forEach(b => b.addEventListener("click", () => { const e = c.evidence[+b.dataset.shot]; from = b;
      lbImg.src = "img/" + e.file; lbImg.alt = e.title; lbCap.textContent = `${e.title}. ${e.caption}${e.hide && e.hide.length ? ". Names and IDs hidden." : ""}`; lb.hidden = false; $("button", lb).focus(); }));
    lbImg.addEventListener("click", () => lbImg.classList.toggle("zoom"));
    $("button", lb).addEventListener("click", close);
    lb.addEventListener("click", e => { if (e.target === lb) close(); });
    addEventListener("keydown", e => { if (e.key !== "Escape") return; if (!lb.hidden) { close(); return; }
      if (opts.embed) try { parent.postMessage({ type: "brandita:close" }, "*"); } catch (_) {} });
  }

  global.CaseEngine = { render, read, plan };
})(window);
