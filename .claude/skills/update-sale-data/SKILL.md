---
name: update-sale-data
description: Run the daily update of the sale tracker. Re-check brands' Black Friday sale status and record product prices on each brand's own site (for the lowest/median/highest price columns and the stats page), using a browser and parallel subagents, then validate, commit and push data/brands.json and data/prices.json.
---

# Daily sale-data update

The daily update has two parts, and both are defined in `AGENTS.md`. Read it first; its rules win if anything here disagrees.

| Part | File | Which brands |
|---|---|---|
| **Sale status**: is a Black Friday sale live? | `data/brands.json` | Brands whose `status` isn't `live` or `closed` |
| **Prices**: what tracked products cost today | `data/prices.json` | Every brand with a US site, including `live` ones, since their prices are what's changing. **Not retailers**: pricing them means too many pages per category |

Only those two files change. Don't edit `index.html`, `stats.html`, the schemas or `scripts/`.

The prices feed two views: on the main page, picking a category adds Lowest, Median and Highest columns per brand, computed from that brand's own products; `stats.html` shows the same three numbers per category across all brands. So every brand needs its own products in each category it sells, not just a few products per category overall.

## 1. Get set up

1. Pull: `git pull --ff-only`. Other sessions push to this repo too.
2. Today's date is US Eastern: `TZ=America/New_York date +%F`.
3. Print what there is to check:

   ```sh
   python3 - <<'PY'
   import json
   from collections import Counter
   b = json.load(open('data/brands.json')); p = json.load(open('data/prices.json'))
   n = Counter((o['brand'], o['category']) for o in p['observations'])
   for i, x in enumerate(b['brands']):
       have = ', '.join(f'{c}:{k}' for (br, c), k in n.items() if br == x['name'])
       print(i, '|', x['name'], '|', x['website'], '|', x['status'], '|', ','.join(x['tags']), '|', x['notes'], '|', have or 'no prices')
   print([c['id'] + ' (' + c['tag'] + ')' for c in p['categories']])
   PY
   ```

4. `python3 scripts/validate.py` prints the current stats per category. Note which categories and brands have few or no products: the price work should fill those first.

## 2. Use a browser on the user's computer

Check sites in a real browser, not WebFetch or search results: WebFetch misses banners and prices that load with JavaScript, and some sites block it. A brand's status and prices come from the brand's own site, and a retailer's status from the retailer's own site; deal roundups and other sellers' listings don't count.

- **Claude in Chrome** (`mcp__claude-in-chrome__*`) is the user's Chrome. It only works while Chrome is open with the extension connected. If `tabs_context_mcp` says it isn't connected, don't keep retrying.
- **The desktop app's built-in browser** (`mcp__remote-devices__Claude_Browser__*`) works whenever the Claude desktop app is open on the user's computer, including when the user is messaging from their phone. Use it when Chrome isn't connected.
- In a scheduled run with no browser on the user's computer, use whatever browser tool the session has, and say in the summary which one you used.

## 3. Split the work across subagents

Launch three subagents in the background at the same time, one per tag group: **apparel**, **road bikes** and **components**. The components subagent also checks the **retailers'** sale status (status only; retailers get no prices). Brands with two tags go to the first group they're in, so no brand is checked twice. Give each one:

1. Today's date, and that Black Friday is the Friday after US Thanksgiving.
2. Which browser tools to use, loaded in one ToolSearch call, and the browser rules below.
3. **Status list**: its brands that aren't `live` or `closed`, as `index | name | website | status | notes`, plus the status table and notes rule from `AGENTS.md`.
4. **Price list**: every brand in its group with a US site (no retailers), the categories of its tags (copy each category's `description`), its existing observations (`url`, `product`, `price`, `full_price`), and the rules from the `AGENTS.md` "What to record" section: US dollars only, up to 3 products per brand per category (cheapest, mid-range, flagship), men's or unisex, the price shown on the product page ignoring codes and checkout-only discounts.
5. The reply format below.

Better starting URLs for sites whose bare domain redirects badly: `https://www.cannondale.com/en-us`, `https://www.canyon.com/en-us/`, `https://www.giant-bicycles.com/us`, `https://pinarello.com/usa/en`, `https://www.trekbikes.com/us/en_US/`, `https://us.santinicycling.com`, `https://us.blacksheep.cc`, `https://www.decathlon.com/collections/van-rysel`, `https://us.muc-off.com/`, `https://ride.shimano.com`, `https://shop.sram.com/`.

### How a subagent finds prices

- **Existing observations first.** Open each `url` and read the price and any crossed-out price. If the page is gone or the product is sold out in every size, report it for removal and suggest a replacement at the same price level.
- **Then fill gaps.** For each brand and category with fewer than 3 products, open the brand's category page (for example Men > Bib shorts), sort by price if the site allows, and take the cheapest, one from the middle, and the most expensive current product. Open each product page to read the exact price; listing pages sometimes show "from" prices.
- Read prices from the page text (`get_page_text` or `find`) rather than screenshots when you can; it avoids misreading digits.
- Skip a brand for prices, and say why, when its site shows no US dollar prices (euros or pounds only, dealer-only, "we don't ship to your country").
- On a big first run, cover every category with a few brands before going deep on any one category.

### Browser rules for subagents

- Three agents share one browser, so each creates its own tab and passes that tab ID to every call. Never close a tab you didn't create. If a tab ID stops working, list the tabs again and open a new one.
- Navigate, then read the page with page text, `find`, or a screenshot (scale 0.5). A redirect can make the next call fail with a "different site" error; list the tabs and try again.
- For status, look past the homepage hero: the top bar, the menu (a "Black Friday" or "Sale" item), and the page a sale banner links to. A collection or page titled "Black Friday" counts as `live` even when the homepage banner just says "Sale".
- Don't accept cookies, sign up, log in, change region, add to cart or type anything. Never try to get past a bot check or CAPTCHA.
- If a site won't load, try once more. If you still can't check a brand (site down, blocked, bot check), report it as couldn't check with the reason and don't change its entries.
- Close your tabs when done.

### Reply format

Ask each subagent to return only one JSON object, followed by an optional short caveats note:

```json
{
  "status": [
    {"index": 52, "name": "Scott", "status": "live", "notes": "Black Friday Sale: up to 50% off bike, winter, moto and more", "changed": true}
  ],
  "prices": {
    "update": [{"url": "https://maap.cc/products/team-bib-evo-black", "price": 180, "full_price": 240}],
    "remove": [{"url": "https://example.com/old-product", "reason": "page gone"}],
    "add": [{"category": "bib-shorts", "brand": "MAAP", "product": "Team Bib Evo", "url": "https://maap.cc/products/team-bib-evo-black", "price": 180, "full_price": 240}]
  },
  "couldnt_check": [{"name": "Pissei", "reason": "bot check"}],
  "no_us_prices": [{"name": "Nalini", "reason": "euro prices only"}]
}
```

`status` entries add `"website"` only if a brand has permanently moved to a new domain. `brand` in price entries must be exactly the brand's `name` in `brands.json`. Prices are plain numbers in US dollars.

Read the caveats: they flag judgment calls, such as a page titled Black Friday behind a banner that isn't, or a product that might belong in another category. Make the call yourself and tell the user about the close ones.

## 4. Apply the changes

Put the three replies into the script below (or save them as JSON files outside the repo and load them), then edit both data files with one script. Never retype the files.

```python
import json, re
TODAY = "YYYY-MM-DD"            # Eastern
replies = [...]                  # the three subagent JSON objects

def load(p):
    raw = open(p, encoding="utf-8").read(); d = json.loads(raw)
    assert json.dumps(d, indent=2, ensure_ascii=False) + "\n" == raw
    return d
def save(p, d):
    open(p, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")

brands = load("data/brands.json"); prices = load("data/prices.json")

# Sale status
for r in replies:
    for u in r["status"]:
        b = brands["brands"][u["index"]]
        assert b["name"] == u["name"], (u["index"], b["name"])   # a stale index must not edit the wrong brand
        if b["status"] == "live":
            continue                                             # live brands are never changed
        b["status"], b["notes"] = u["status"], u["notes"]
        if "website" in u:
            b["website"] = u["website"]
        if b["status"] == "live" and b["detected"] is None:
            b["detected"] = TODAY                                # set once, never changed
brands["checked"] = TODAY

# Prices
obs = {o["url"]: o for o in prices["observations"]}
for r in replies:
    p = r["prices"]
    for u in p["update"]:
        o = obs[u["url"]]
        o["price"], o["full_price"], o["date"] = u["price"], u["full_price"], TODAY
    for u in p["remove"]:
        obs.pop(u["url"], None)
    for a in p["add"]:
        if a["url"] in obs:                                      # already tracked: treat as an update
            obs[a["url"]].update(price=a["price"], full_price=a["full_price"], date=TODAY)
        else:
            obs[a["url"]] = {**{k: a[k] for k in ("category", "brand", "product", "url", "price", "full_price")}, "date": TODAY}
prices["observations"] = sorted(obs.values(), key=lambda o: (
    [c["id"] for c in prices["categories"]].index(o["category"]), o["brand"], o["price"]))
prices["checked"] = TODAY

save("data/brands.json", brands); save("data/prices.json", prices)
```

Then run `python3 scripts/validate.py`. It checks both files (including that each price's brand exists, isn't a retailer and carries the category's tag, and the 3-per-brand limit) and prints the stats as the page will show them. Fix what it reports. If a lowest or highest value looks out of line, check that product's category and price before committing. Finally check that `git diff --stat` lists only the two data files.

## 5. Commit and push

Commit only `data/brands.json` and `data/prices.json`, using the message format in `AGENTS.md`: the new Black Friday sales, other status changes, a `Prices:` line (products checked, added, removed, and how many are on sale), and a `Couldn't check` line for sites that didn't load (leave it out if every site loaded).

If git has no identity configured, reuse the previous commit's author for this one commit instead of changing the config:

```sh
git -c user.name="$(git log -1 --format=%an)" -c user.email="$(git log -1 --format=%ae)" commit -F msg.txt
```

Then `git push origin master`. Pushing publishes the GitHub Pages site. If the push is rejected because someone else pushed, `git pull --rebase` and push again; never force-push.

### Working from the desktop app's shell

When the repo is reached through the Claude desktop app's connected-folder shell:

- **Push is blocked.** That shell can fetch from GitHub but not push. Commit locally, then ask the user to run `git push` from their own Terminal, or to approve another way to push.
- **Git leaves lock files behind** unless file deletion is allowed in the connected folder. Ask for delete permission before committing. If a `.lock` file from an earlier command is left under `.git`, move it aside (for example `mv .git/objects/maintenance.lock .git/stale-maintenance-lock`) rather than deleting it, and only if no git command is still running.

## 6. Report to the user

Summarize: brands that newly went live, other status changes, how many products were priced (and how many are on sale), categories and brands that still have few products, brands skipped for having no US prices, sites you couldn't check, and judgment calls. Give the commit hash and say whether it's pushed.
