# datalidy.com

Marketing site for **Datalidity**, a data-driven, social-impact advisory and consulting firm.

## How it works

- `content/*.json` holds all page copy (practices, services, industries, insights). `content/taxonomy.json` defines the slugs and order.
- `static/` holds the stylesheet, script and images (photography from Pexels).
- `build.py` (Python 3, standard library only) generates the full static site into `docs/` and fails if any internal link is broken.
- GitHub Pages serves `docs/` from the `main` branch at `amne51ac.github.io/datalidy`.
- A Cloudflare Worker (`worker/`) bound to `datalidy.com` and `www.datalidy.com` serves that GitHub Pages site at the domain root, redirects `www` to the apex, and adds security headers.

## Editing

```sh
python3 build.py                     # rebuild docs/
python3 -m http.server -d docs 8000  # preview at http://localhost:8000
git commit -am "Update content" && git push   # GitHub Pages redeploys automatically
```

To add a service, add its slug to `content/taxonomy.json` and its entry to the matching `content/services_*.json`, then rebuild.

The Worker only needs redeploying if `worker/` changes:

```sh
cd worker && npx wrangler deploy
```
