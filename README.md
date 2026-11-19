# Cycling Sale Tracker

A static page (GitHub Pages) that tracks Black Friday sales at road cycling brands and retailers.

```
index.html                 the page: loads the data, renders sortable, searchable tables
data/index.json            manifest: page title and the table files to show, in order
data/apparel.json          one file per table
data/road-bikes.json
data/components.json
data/retailers.json
data/table.schema.json     JSON Schema for a table file
data/index.schema.json     JSON Schema for the manifest
```

## Updating the data

Edit only the files in `data/`. The page needs no changes.

Each table file has a `title`, a `checked` date, the `columns` to display, and `rows`. When you check a table, set its `checked` to that date (`YYYY-MM-DD`).

Every row has these fields:

- `name`: brand or retailer name
- `website`: full URL, or `null`
- `status`: one of
  - `live`: a Black Friday sale is live
  - `other_sale`: some other sale is on
  - `not_yet`: no sale
  - `unknown`: couldn't check the site
  - `closed`: no longer operates
- `detected`: the date (`YYYY-MM-DD`) the Black Friday sale was **first** seen live. Set it the first day `status` becomes `live`, and don't change it after that. Leave it `null` until then.
- `notes`: what was seen on the site

Any other fields (such as `type`, `country`, `ships_from`) are free text and are shown if they're listed in `columns`.

To add a table, create a new file in `data/` following `table.schema.json` and add its filename to `tables` in `data/index.json`.

Keep files valid JSON: 2-space indent, UTF-8, trailing newline.

## Previewing locally

The page loads its data with `fetch`, so opening `index.html` straight from disk won't work. Serve the folder:

```sh
python3 -m http.server
# then open http://localhost:8000
```
