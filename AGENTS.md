# Instructions for agents

This repo is a static GitHub Pages site that tracks Black Friday sales at road cycling brands and retailers. Pushing to `master` publishes it.

**A data update edits only `data/brands.json` and `data/prices.json`.** Their formats are defined in `data/brands.schema.json` and `data/prices.schema.json`. Don't change `index.html`, `stats.html`, the schemas or `scripts/` as part of a data update.

The daily update has two parts: the sale **status** of each brand (`brands.json`) and the **prices** of tracked products (`prices.json`, see [Prices](#prices)).

## Daily update

All dates ("today", `checked`, `detected`, the commit title) are in US Eastern time (`America/New_York`), not UTC. Get today's date with `TZ=America/New_York date +%F`.

1. Open `data/brands.json`.
2. Skip brands whose `status` is already `live`: their sale is established, so don't recheck them or change their entry.
3. For each other brand, visit its `website` (the homepage, plus any sale or Black Friday page linked from it) and update:
   - `status`: see the table below.
   - `notes`: one short, factual sentence about what's on the site. Include the discount, any code, and any end date shown, e.g. `Black Friday: 25% off sitewide plus free shipping` or `Up to 33% off selected styles until Nov 26`. If nothing changed since the last check, leave the notes as they are.
   - `detected`: if `status` is now `live` and `detected` is `null`, set it to today's date. **Never change `detected` once it's set**, even if the sale ends.
4. If you can't check a brand (the site is down, blocks you, or shows a bot check), leave its entry exactly as it is. Don't set it to `unknown` or rewrite its notes; list it in the commit message instead (see below). Never try to get past bot checks.
5. Set the top-level `checked` to today's date (`YYYY-MM-DD`, Eastern time).
6. Update prices in `data/prices.json` (see [Prices](#prices)). Unlike step 2, this covers `live` brands too, since their prices are what's changing.
7. Validate (see below), then commit and push.

### Status values

| `status` | Use when |
|---|---|
| `live` | A sale explicitly called Black Friday (or Black Week, BFCM, Cyber Week, etc.) is live |
| `other_sale` | Some other sale is on (clearance, holiday, "annual sale", archive sale promoted on the homepage) |
| `not_yet` | No sale on the site, or only a standing Sale section that isn't promoted |
| `unknown` | Not used by the daily update. A failed check leaves the entry unchanged and goes in the commit message instead. |
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

## Prices

`data/prices.json` tracks prices of individual products on each brand's own site. Retailers aren't priced (it would mean too many pages to check); they only get a sale status. The site computes the **lowest, median and highest** price (and the full price behind any sale) from them in two places:

- **Main page (`index.html`):** picking a category in "Prices for" adds Lowest, Median and Highest columns to the table, one row per brand, from that brand's own products.
- **Stats page (`stats.html`):** the same three numbers per category across every brand.

You only record the products; the pages do the math.

### Categories

The top-level `categories` list defines what's tracked. Each has an `id`, a `label`, the brand `tag` it belongs to (`apparel`, `road-bikes` or `components`), and a `description` of what counts. Read the description before adding a product: for example, bib shorts are men's or unisex bib shorts with straps, and wheelsets are carbon road wheelsets sold as a pair.

Don't rename, reorder or remove categories as part of a data update; the page shows them in this order. If the user asks for a new category, add it at the end of its tag's group.

### Observations

Each entry in `observations` is one product:

```json
{
  "category": "bib-shorts",
  "brand": "MAAP",
  "product": "Team Bib Evo",
  "url": "https://maap.cc/products/team-bib-evo-black",
  "price": 180,
  "full_price": 240,
  "date": "2026-11-20"
}
```

- `category`: a category `id`.
- `brand`: exactly the brand's `name` in `brands.json`. The brand must have the category's tag there (so POC, tagged `apparel` and `components`, can have helmets and jackets). Don't record prices for retailers (tag `retailer`).
- `product`: the product name as the site shows it.
- `url`: the product page the price came from. Each product appears once.
- `price`: what it costs today on the product page, in US dollars, including any sale price shown there. Ignore discount codes, member-only prices, bundles and discounts that only appear at checkout.
- `full_price`: the regular price (the crossed-out one). If the product isn't discounted, the same as `price`.
- `date`: the date (Eastern) you last saw this price.

### What to record

- **US prices only.** Use the brand's US site, in US dollars. If a brand has no US pricing (euros only, no shipping to the US, dealer-only), skip it; don't convert currencies.
- **Up to 3 products per brand per category**: the cheapest, a mid-range one, and the flagship of the brand's current range in that category. Use the standard men's or unisex version; skip kids', women's-only duplicates of the same product, and limited-edition prints.
- **Brands only.** Record prices only from a brand's own site. Skip retailers, and don't take a brand's price from a retailer's listing.
- **Sizes and colors:** use the price shown for the product before choosing a size. If colors are priced differently, use the regular color, not the discounted leftover.
- A brand only needs products in the categories it actually sells.

### Daily price update

1. For **every** existing observation (whatever the brand's status), open its `url` and update `price`, `full_price` and `date`. Keep `product` and `url` unless the product was renamed.
2. If the product page is gone or the product is sold out in every size, remove the observation and, if the brand still sells something in that category, add a replacement at the same price level.
3. Fill gaps: for brands with fewer than 3 products in a category they sell, add more (see above). Spread effort so every category builds up a few brands rather than one category getting dozens.
4. If you can't load a brand's site, leave its observations as they are (their `date` shows they're stale) and list the brand in the commit message's `Couldn't check` line.
5. Set the top-level `checked` in `prices.json` to today's date.

Edit `prices.json` with a script (read the JSON, change it, write it with 2-space indent, `ensure_ascii=False` and a trailing newline), not by retyping it.

## Validate before committing

```sh
python3 scripts/validate.py
```

It checks both files and prints the lowest, median and highest price per category, as the page will show them. It checks that:

- both files keep their formatting (2-space indent, UTF-8, trailing newline)
- every `status` is one of the five values above
- every `detected` is `null` or a `YYYY-MM-DD` date, and every `live` brand has one
- every tag id used by a brand is defined in the top-level `tags`
- `website` values start with `https://` (or are `null`)
- every price observation uses a known category, a brand from `brands.json` with that category's tag, a unique `https://` URL, positive prices with `full_price` at least `price`, and a valid `date`
- no brand has more than 3 products in one category

Fix anything it reports before committing. Glance at the printed stats too: a "lowest" or "highest" far out of line usually means a wrong category or a misread price.

To see the result, serve the folder with `python3 -m http.server` and open http://localhost:8000.

## Commit

Commit only `data/brands.json` and `data/prices.json`, with a message like:

```
Update sale data for 2026-11-19

New Black Friday sales: Rapha, Gobik
Other changes: Sportful sale ended
Prices: 212 products checked, 14 added, 3 removed; 61 on sale
Couldn't check: POC (bot check), REI (site down)
```

Leave out the `Couldn't check` line if every site loaded.

Then push to `master`.
