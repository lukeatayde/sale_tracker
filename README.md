# Cycling Sale Tracker

A static page (GitHub Pages) that tracks Black Friday sales at road cycling brands and retailers.

```
index.html                 the page: price stats by category, then one sortable, searchable table with tag filters
data/brands.json           each brand's Black Friday sale status
data/prices.json           tracked product prices, for the lowest/median/highest stats per category
data/*.schema.json         JSON Schemas for the two data files
scripts/validate.py        checks both data files and prints the price stats
AGENTS.md                  how to update the data
.claude/skills/            the update-sale-data skill for running the daily update
```

## Updating the data

Edit only `data/brands.json` and `data/prices.json`, then run `python3 scripts/validate.py`; the page picks up changes automatically. See [AGENTS.md](AGENTS.md) for the field reference, status definitions and update steps.

## Previewing locally

The page loads its data with `fetch`, so opening `index.html` straight from disk won't work. Serve the folder:

```sh
python3 -m http.server
# then open http://localhost:8000
```
