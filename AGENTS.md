# Instructions for agents

This repo is a static GitHub Pages site that tracks Black Friday sales at road cycling brands and retailers. Pushing to `master` publishes it.

**The only file you should edit is `data/brands.json`.** Its format is defined in `data/brands.schema.json`. Don't change `index.html` or the schema as part of a data update.

## Daily update

1. Open `data/brands.json`.
2. For each brand, visit its `website` (the homepage, plus any sale or Black Friday page linked from it) and update:
   - `status`: see the table below.
   - `notes`: one short, factual sentence about what's on the site. Include the discount, any code, and any end date shown, e.g. `Black Friday: 25% off sitewide plus free shipping` or `Up to 33% off selected styles until Nov 26`. If nothing changed since the last check, leave the notes as they are.
   - `detected`: if `status` is now `live` and `detected` is `null`, set it to today's date. **Never change `detected` once it's set**, even if the sale ends.
3. Set the top-level `checked` to today's date (`YYYY-MM-DD`).
4. Validate (see below), then commit and push.

### Status values

| `status` | Use when |
|---|---|
| `live` | A sale explicitly called Black Friday (or Black Week, BFCM, Cyber Week, etc.) is live |
| `other_sale` | Some other sale is on (clearance, holiday, "annual sale", archive sale promoted on the homepage) |
| `not_yet` | No sale on the site, or only a standing Sale section that isn't promoted |
| `unknown` | You couldn't check: the site was down, blocked you, or showed a bot check. Say which in `notes`. Never try to get past bot checks. |
| `closed` | The brand no longer operates |

## Brand fields

```json
{
  "name": "Castelli",
  "website": "https://castelli-cycling.com",
  "status": "live",
  "detected": "2026-11-18",
  "tags": ["apparel"],
  "type": "Performance",
  "notes": "Black Friday early access: 25% off the collection when you sign up",
  "country": "Italy"
}
```

- `name`: brand or retailer name.
- `website`: full URL (`https://...`), or `null` if there isn't one.
- `tags`: one or more ids from the top-level `tags` list (`apparel`, `road-bikes`, `components`, `retailer`).
- `type`: what the brand makes or sells. Put several values in one string separated by `; `, e.g. `"Modern premium; Helmets & eyewear"`. Each value appears on the page as its own colored label, so reuse existing wording exactly (`Modern premium`, not `modern premium` or `Modern/premium`).
- `country`: home country, or for retailers where they ship from.

## Rules

- **One entry per brand.** If a brand fits more than one category, give it more than one tag; don't add it twice.
- **Don't reorder brands.** Add new brands at the end of `brands`. Label colors are assigned in order of first appearance, so reordering changes them.
- **Don't rename or reorder tags** in the top-level `tags` list; the page uses that order for checkboxes and colors. To add a category, add a new tag at the end with an `id` (lowercase, hyphens) and a `label`.
- Don't delete brands that close. Set `status` to `closed` and explain in `notes`.
- Keep the file formatting: 2-space indent, UTF-8 (write `é`, not `é`), trailing newline.

## Validate before committing

```sh
python3 -m json.tool data/brands.json > /dev/null && echo "valid JSON"
```

Then check that:

- every `status` is one of the five values above
- every `detected` is `null` or a `YYYY-MM-DD` date, and every `live` brand has one
- every tag id used by a brand is defined in the top-level `tags`
- `website` values start with `https://` (or are `null`)

To see the result, serve the folder with `python3 -m http.server` and open http://localhost:8000.

## Commit

Commit only `data/brands.json`, with a message like:

```
Update sale data for 2026-11-19

New Black Friday sales: Rapha, Gobik
Other changes: Sportful sale ended
```

Then push to `master`.
