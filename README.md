# Cycling Sale Tracker

A static page (GitHub Pages) that tracks Black Friday sales at road cycling brands and retailers.

```
index.html                 the page: one sortable, searchable table with tag filters
data/brands.json           the data (the only file that changes day to day)
data/brands.schema.json    JSON Schema describing brands.json
AGENTS.md                  how to update the data
```

## Updating the data

Edit only `data/brands.json`; the page picks up changes automatically. See [AGENTS.md](AGENTS.md) for the field reference, status definitions and update steps.

## Previewing locally

The page loads its data with `fetch`, so opening `index.html` straight from disk won't work. Serve the folder:

```sh
python3 -m http.server
# then open http://localhost:8000
```
