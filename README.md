# Cycling Sale Tracker

A static page (GitHub Pages) that tracks Black Friday sales at road cycling apparel brands.

```
index.html                 the page: loads the data and renders a sortable table
data/brands.json           the data (the only file that changes day to day)
data/brands.schema.json    JSON Schema describing brands.json
```

## Updating the data

Edit only `data/brands.json`. The page needs no changes.

- Set `checked` to the date of the check (`YYYY-MM-DD`).
- Each entry in `brands` has: `brand`, `website` (full URL or `null`), `status`, `notes`, `country`, `type`.
- `status` must be one of:
  - `live`: a Black Friday sale is live
  - `other_sale`: some other sale is on
  - `not_yet`: no sale
  - `unknown`: couldn't check the site
  - `closed`: the brand no longer operates
- `type` must be one of the values listed in `data/brands.schema.json`.
- Keep the file valid JSON: 2-space indent, UTF-8, trailing newline.

## Previewing locally

The page loads its data with `fetch`, so opening `index.html` straight from disk won't work. Serve the folder:

```sh
python3 -m http.server
# then open http://localhost:8000
```
