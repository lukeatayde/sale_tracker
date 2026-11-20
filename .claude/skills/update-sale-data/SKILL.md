---
name: update-sale-data
description: Re-check brands in data/brands.json for Black Friday sales using the browser on the user's computer, with subagents working in parallel, then validate, commit and push. Use for the daily sale-data update.
---

# Daily sale-data update

This skill runs the daily update described in `AGENTS.md`. Read `AGENTS.md` first; its status definitions, field rules and validation checks apply here. The only file this update changes is `data/brands.json`.

## 1. Get set up

1. Pull first: `git pull --ff-only`. The user may have pushed from their own machine.
2. Use today's date in US Eastern time, as `AGENTS.md` requires: `TZ=America/New_York date +%F`.
3. List the brands with their index, name, website, status and notes:

   ```sh
   python3 -c "
   import json; d = json.load(open('data/brands.json'))
   for i, b in enumerate(d['brands']):
       print(i, '|', b['name'], '|', b['website'], '|', b['status'], '|', ','.join(b['tags']), '|', b['notes'])
   "
   ```

## 2. Decide what to check

Re-check only brands that **haven't released a Black Friday sale yet**: any status except `live` and `closed`. `AGENTS.md` says to skip `live` brands; re-check them only if the user asks.

## 3. Check the sites in a browser on the user's computer

The checks must use a real browser on the user's computer, not WebFetch or search results. WebFetch misses banners that load with JavaScript, and some sites block it. Sale banners and retailer deal roundups don't count; only what the brand's own site shows does.

- **Claude in Chrome** (`mcp__claude-in-chrome__*`) is the user's own Chrome. It only works while Chrome is open on their computer with the extension connected. If `tabs_context_mcp` says the extension isn't connected, don't keep retrying.
- **The desktop app's built-in browser** (`mcp__remote-devices__Claude_Browser__*`) works whenever the Claude desktop app is open on the user's computer, including when the user is messaging from their phone. Use it when Chrome isn't connected.

Split the brands across three subagents, one per tag group: apparel, road bikes, and components plus retailers. Launch them in the background at the same time. Give each one:

- today's date, and that Black Friday is the Friday after US Thanksgiving
- which browser tools to use, loaded in one ToolSearch call
- the brands to check, as `index | name | website | status | notes`, with a better URL in parentheses where the bare domain redirects badly. Known ones: `https://www.cannondale.com/en-us`, `https://www.canyon.com/en-us/`, `https://www.giant-bicycles.com/us`, `https://pinarello.com/usa/en`, `https://www.trekbikes.com/us/en_US/`, `https://us.santinicycling.com`, `https://us.blacksheep.cc`, `https://www.decathlon.com/collections/van-rysel`, `https://us.muc-off.com/`, `https://ride.shimano.com`, `https://shop.sram.com/`
- the status table from `AGENTS.md`, and the notes rule: one short factual sentence with the discount, any code and any end date; if nothing changed, keep the old notes word for word
- the browser rules below
- the reply format below

### Browser rules for subagents

- Three agents share one browser, so each creates its own tab and passes that tab ID to every call. Never close a tab you didn't create. If a tab ID stops working, list the tabs again and open a new one.
- Navigate, then read the page with a screenshot (scale 0.5) or page text. A redirect can make the next call fail with a "different site" error; list the tabs and try again.
- Look past the homepage hero: check the top bar, the menu (a "Black Friday" or "Sale" item), and the page a sale banner links to. A collection or page titled "Black Friday" counts as `live` even when the homepage banner just says "Sale".
- Don't accept cookies, sign up, log in, change region or type anything. Never try to get past a bot check or CAPTCHA.
- If a site won't load, try once more. If you still can't check a brand (site down, blocked, bot check), report it as couldn't check with the reason; don't change its status or notes.
- Close your tabs when done.

### Reply format

Ask each subagent to return only a JSON array, one object per brand, followed by an optional short caveats note:

```json
[{"index": 52, "name": "Scott", "status": "live", "notes": "Black Friday Sale: up to 50% off bike, winter, moto and more", "changed": true}]
```

Add `"website"` only if a brand has permanently moved to a new domain. List brands you couldn't check separately, as `{"index": 35, "name": "Pissei", "couldnt_check": "bot check"}`, so the coordinator leaves their entries untouched. Read the caveats: they flag judgment calls, such as a page titled Black Friday behind a banner that isn't. Make the call yourself, and tell the user about the close ones.

## 4. Apply the changes

Edit the file with a script, never by retyping it. Keep the formatting: 2-space indent, real UTF-8 characters, trailing newline. Check the name at each index so a stale index can't edit the wrong brand.

```python
import json, re
p = 'data/brands.json'
raw = open(p, encoding='utf-8').read()
d = json.loads(raw)
assert json.dumps(d, indent=2, ensure_ascii=False) + "\n" == raw  # formatting will survive a rewrite

TODAY = "YYYY-MM-DD"
updates = {  # index: (expected name, status, notes)
    52: ("Scott", "live", "Black Friday Sale: up to 50% off bike, winter, moto and more"),
}
for i, (name, status, notes) in updates.items():
    b = d['brands'][i]
    assert b['name'] == name, (i, b['name'])
    b['status'], b['notes'] = status, notes
    if status == 'live' and b['detected'] is None:
        b['detected'] = TODAY  # set once; never change an existing date
d['checked'] = TODAY
open(p, 'w', encoding='utf-8').write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")

tags = {t['id'] for t in d['tags']}
for b in d['brands']:
    assert b['status'] in {"live", "other_sale", "not_yet", "unknown", "closed"}
    assert b['detected'] is None or re.fullmatch(r"\d{4}-\d{2}-\d{2}", b['detected'])
    assert b['status'] != 'live' or b['detected']
    assert set(b['tags']) <= tags
    assert b['website'] is None or b['website'].startswith('https://')
```

Then run `python3 -m json.tool data/brands.json > /dev/null && echo "valid JSON"` and check `git diff --stat` shows only `data/brands.json`.

## 5. Commit and push

Commit only `data/brands.json`, using the message format in `AGENTS.md`: list the new Black Friday sales, the other changes, and a `Couldn't check` line for brands whose sites didn't load (leave it out if every site loaded).

If git has no identity configured, reuse the previous commit's author for this one commit instead of changing the config:

```sh
git -c user.name="$(git log -1 --format=%an)" -c user.email="$(git log -1 --format=%ae)" commit -F msg.txt
```

Then `git push origin master`. Pushing publishes the GitHub Pages site.

### Working from the desktop app's shell

When the repo is reached through the Claude desktop app's connected-folder shell:

- **Push is blocked.** That shell can fetch from GitHub but not push. Commit locally, then ask the user to run `git push` from their own Terminal, or to approve another way to push.
- **Git leaves lock files behind** unless file deletion is allowed in the connected folder. Ask for delete permission before committing. If a `.lock` file from an earlier command is left under `.git`, move it aside (for example `mv .git/objects/maintenance.lock .git/stale-maintenance-lock`) rather than deleting it, and only if no git command is still running.

## 6. Report to the user

Summarize which brands newly went live, other status changes, brands you couldn't check, and any judgment calls. Give the commit hash, and say whether it's pushed.
