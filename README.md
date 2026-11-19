# Cycling Sale Tracker

A static page (GitHub Pages) that tracks Black Friday sales at road cycling brands and retailers.

```
index.html                 the page: merges all tables into one sortable, searchable table
                           with a checkbox per category and an "on sale now" filter
data/index.json            manifest: page title and the category files to show, in order
data/apparel.json          one file per category
data/road-bikes.json
data/components.json
data/retailers.json
data/table.schema.json     JSON Schema for a table file
data/index.schema.json     JSON Schema for the manifest
```

## Updating the data

Edit only the files in `data/`. The page needs no changes.

Each table file is one category on the page. It has a `title` (the category name), a `checked` date, the `columns` to display, and `rows`. When you check a table, set its `checked` to that date (`YYYY-MM-DD`). The page shows the most recent `checked` date across all tables.

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

Any other fields (such as `type`, `country`) are free text and are shown if they're listed in `columns`. All tables are merged into one table on the page, so use the same key for the same kind of field across files (for example, retailers use `country` for where they ship from).

The "On sale now" filter shows rows whose status is `live` or `other_sale`.

To add a table, create a new file in `data/` following `table.schema.json` and add its filename to `tables` in `data/index.json`.

Keep files valid JSON: 2-space indent, UTF-8, trailing newline.

## Previewing locally

The page loads its data with `fetch`, so opening `index.html` straight from disk won't work. Serve the folder:

```sh
python3 -m http.server
# then open http://localhost:8000
```
