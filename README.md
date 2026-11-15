# Brandita — the built site

The live site is **https://brandita.net/**, hosted on Hostinger: hPanel → Git deploys this repo's `main`
branch into `public_html`. This repo holds the built site only; the source is the private Next.js app
`Official-7amdy/brandita-web`, built with `npm run build:hostinger` and copied here.

- `.htaccess`, `ar/.htaccess`, `_next/static/.htaccess`: https, language redirect, the forms' route,
  the old site's addresses, 404 pages, caching.
- `api/index.php`: the consultation form's email. Its settings (`brandita-config.php`) live outside
  `public_html` on the server, never in this repo.

The old GitHub Pages address (official-7amdy.github.io/brandita-work) forwards every page to the same
page on brandita.net.
