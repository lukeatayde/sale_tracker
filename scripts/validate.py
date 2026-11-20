#!/usr/bin/env python3
"""Check data/brands.json and data/prices.json, then print price stats per category.

Run from the repo root before committing:

    python3 scripts/validate.py

Exits non-zero and lists every problem if a check fails.
"""
import json
import re
import statistics
import sys
from collections import Counter, defaultdict

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STATUSES = {"live", "other_sale", "not_yet", "unknown", "closed"}
MAX_PER_BRAND = 3  # products per brand per category

errors = []


def check(ok, msg):
    if not ok:
        errors.append(msg)


def load(path):
    raw = open(path, encoding="utf-8").read()
    data = json.loads(raw)
    check(raw == json.dumps(data, indent=2, ensure_ascii=False) + "\n",
          f"{path}: formatting changed (use 2-space indent, real UTF-8 characters, trailing newline)")
    return data


brands = load("data/brands.json")
prices = load("data/prices.json")

# ---- brands.json ----
tag_ids = {t["id"] for t in brands["tags"]}
check(DATE.match(brands.get("checked") or ""), "brands.json: `checked` must be YYYY-MM-DD")
names = Counter(b["name"] for b in brands["brands"])
for n, c in names.items():
    check(c == 1, f"brands.json: {n} appears {c} times")
for b in brands["brands"]:
    n = b["name"]
    check(b["status"] in STATUSES, f"{n}: unknown status {b['status']!r}")
    check(b["detected"] is None or DATE.match(b["detected"]), f"{n}: `detected` must be null or YYYY-MM-DD")
    check(b["status"] != "live" or b["detected"], f"{n}: live but `detected` is null")
    check(set(b["tags"]) <= tag_ids, f"{n}: tag not defined at the top: {set(b['tags']) - tag_ids}")
    check(b["website"] is None or b["website"].startswith("https://"), f"{n}: website must start with https://")

# ---- prices.json ----
brand_by_name = {b["name"]: b for b in brands["brands"]}
cats = {c["id"]: c for c in prices["categories"]}
check(prices["currency"] == "USD", "prices.json: currency must be USD")
check(prices["checked"] is None or DATE.match(prices["checked"]), "prices.json: `checked` must be null or YYYY-MM-DD")
for c in prices["categories"]:
    check(c["tag"] in tag_ids, f"category {c['id']}: tag {c['tag']!r} isn't a tag in brands.json")

urls = Counter(o["url"] for o in prices["observations"])
per_brand = Counter((o["category"], o["brand"]) for o in prices["observations"])
for o in prices["observations"]:
    where = f"{o.get('brand')} / {o.get('product')}"
    check(o["category"] in cats, f"{where}: unknown category {o['category']!r}")
    check(o["brand"] in brand_by_name, f"{where}: brand isn't a `name` in brands.json")
    if o["brand"] in brand_by_name and o["category"] in cats:
        b = brand_by_name[o["brand"]]
        check(cats[o["category"]]["tag"] in b["tags"],
              f"{where}: brand isn't tagged {cats[o['category']]['tag']!r} in brands.json")
    check(o["url"].startswith("https://"), f"{where}: url must start with https://")
    check(urls[o["url"]] == 1, f"{where}: url is used by more than one observation")
    for k in ("price", "full_price"):
        check(isinstance(o[k], (int, float)) and not isinstance(o[k], bool) and o[k] > 0,
              f"{where}: {k} must be a positive number")
    if isinstance(o["price"], (int, float)) and isinstance(o["full_price"], (int, float)):
        check(o["full_price"] >= o["price"], f"{where}: full_price is lower than price")
    check(DATE.match(o["date"] or ""), f"{where}: date must be YYYY-MM-DD")
    if prices["checked"] and DATE.match(o["date"] or ""):
        check(o["date"] <= prices["checked"], f"{where}: date is after the top-level `checked`")
for (cat, brand), n in per_brand.items():
    check(n <= MAX_PER_BRAND, f"{brand}: {n} products in {cat} (max {MAX_PER_BRAND})")

if errors:
    print("FAILED:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print(f"OK: {len(brands['brands'])} brands, {len(prices['observations'])} price observations")

# ---- stats, as the page shows them ----
by_cat = defaultdict(list)
for o in prices["observations"]:
    by_cat[o["category"]].append(o)


def fmt(v):
    return f"${v:,.0f}"


print(f"\n{'Category':32} {'n':>3} {'brands':>6}  {'low':>8} {'median':>8} {'high':>8}   (full price low / median / high)")
for c in prices["categories"]:
    obs = by_cat.get(c["id"], [])
    if not obs:
        print(f"{c['label']:32} {0:>3} {0:>6}  no prices yet")
        continue
    p = [o["price"] for o in obs]
    f = [o["full_price"] for o in obs]
    nb = len({o["brand"] for o in obs})
    print(f"{c['label']:32} {len(obs):>3} {nb:>6}  {fmt(min(p)):>8} {fmt(statistics.median(p)):>8} {fmt(max(p)):>8}"
          f"   ({fmt(min(f))} / {fmt(statistics.median(f))} / {fmt(max(f))})")
