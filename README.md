# Brandita — work

Case studies and landing pages for Brandita for Digital Services, Cairo.
Live: https://official-7amdy.github.io/brandita-work/

## Pages
- `case-studies.html` — case stories (English). A story playing on one case: `case-studies.html#play-<id>`; a full case in the sheet: `#<id>`
- `case-<id>.html` — the full case, built by the case engine (see below)
- `case-studies-ar.html` — Arabic edition
- `for-stores.html` — landing page for online stores (`#fashion`, `#beauty`, `#food`, `#electronics`)
- `client-case.html` — single client case (`#nour`, `#kahwa` are samples)

## The case engine (`engine/`)
`engine/cases/<id>.json` is the case file. `build_cases.py` checks it (a real client needs `approved: true`; series rows must add up to their totals), burns the screenshot redactions listed under `evidence[].hide`, and writes `case-<id>.html`. The engine reads the file, works out what follows from it (growth multiples, the peak and the dip, how far story hooks beat static ones, margins) and builds only the chapters the data supports: brief, before, the run, the work, the creative, the evidence (store dashboard, ad ledger, screenshot wall), the result, what did not work.

Unredacted screenshots are never committed; redaction runs from a private folder outside this repo.

Only Lazoomi is a real client, published with written approval. Every other case is a marked sample with placeholder figures.