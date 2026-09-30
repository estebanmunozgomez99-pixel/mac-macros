"""Download McMaster's menu from macnutrition.mcmaster.ca (the site McMaster Hospitality said we can use).

The page is an ASP.NET DevExpress app: /Nutrition/ServiceMenuReport/Today lists locations and stations; each
station has a GUID (packed in the navUnits control's base64 'itemsInfo', in the same order as the rendered
station links), and POSTing to /Nutrition/ServiceMenuReport/GetReport/<guid> returns that station's items.

  python3 scripts/fetch_macnutrition.py CSV         fetch today's menu and write it to CSV, if it passes the checks
  python3 scripts/fetch_macnutrition.py --raw DIR   save the raw pages (for working out the report format)

Safety checks before CSV is replaced (a failed check exits 1 and leaves the old file alone): at least 800 items,
every location that's in the current CSV still present, and no more than 20% of the current items gone.
"""
import base64, csv, html, http.cookiejar, os, re, sys, time, urllib.parse, urllib.request

BASE = "https://macnutrition.mcmaster.ca/Nutrition/ServiceMenuReport"
UA = "Mozilla/5.0 (Maroon campus macro app menu updater; contact esteban.munoz.gomez99@gmail.com)"
GUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def get(url, data=None, tries=3):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=body, headers={"User-Agent": UA, "X-Requested-With": "XMLHttpRequest"} if data is not None else {"User-Agent": UA})
            with opener.open(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            if i == tries - 1: raise
            time.sleep(5 * (i + 1))

def stations(page):
    """[(location, station, guid)] in page order."""
    info = re.search(r"MVCxClientNavBar,'navUnits'.*?'itemsInfo':'([^']+)'", page, re.S)
    if not info: raise SystemExit("navUnits not found: the site layout changed")
    guids = list(dict.fromkeys(re.findall(GUID, base64.b64decode(info.group(1)).decode("latin-1"))))
    nav = page[page.find('id="navUnits"'):]
    nav = nav[:nav.find("<script")]
    out, loc = [], None
    for m in re.finditer(r'class="(dxnb-header|dxnb-item)[^"]*"[^>]*>(.*?)</(?:div|li|a)>', nav, re.S):
        text = html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        if not text: continue
        if m.group(1) == "dxnb-header": loc = text
        else: out.append((loc, text))
    if len(out) != len(guids): raise SystemExit(f"{len(out)} stations but {len(guids)} ids: the site layout changed")
    return [(l, s, g) for (l, s), g in zip(out, guids)]

COLS = ["Location", "Station", "Category", "Menu Item", "Serving Size", "Price", "Calories", "Fat (g)", "Saturated Fat (g)",
        "Cholesterol (mg)", "Sodium (mg)", "Carbohydrate (g)", "Total Fibre (g)", "Sugars (g)", "Protein (g)",
        "Vitamin C (mg)", "Calcium (mg)", "Iron (mg)"]

def cell(x): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", x))).strip()

def parse_report(loc, station, page):
    """Rows (same columns as data/sources/mcmaster-menu-week.csv) from one GetReport page."""
    heads = [cell(h).replace("}", ")") for h in re.findall(r"<th[^>]*>(.*?)</th>", page, re.S)]
    if heads and heads != COLS[3:]: raise SystemExit(f"{loc} / {station}: columns changed: {heads}")
    rows, cat = [], ""
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if len(tds) == 1 and "courseHeader" in tr: cat = cell(tds[0]); continue
        if len(tds) == len(COLS) - 3:
            vals = [cell(t) for t in tds]
            vals[3:] = [v.replace(",", "") for v in vals[3:]]  # "3,461" -> "3461", like the original export
            rows.append([loc, station, cat] + vals)
    return rows

def fetch_all():
    page = get(BASE + "/Today")
    rows = []
    for loc, st, g in stations(page):
        rows += parse_report(loc, st, get(f"{BASE}/GetReport/{g}", {"allergens": "", "tags": ""}))
        time.sleep(1)  # be gentle with McMaster's server
    return rows

if __name__ == "__main__":
    if sys.argv[1:2] == ["--raw"]:
        d = sys.argv[2]; os.makedirs(d, exist_ok=True)
        page = get(BASE + "/Today")
        sts = stations(page)
        with open(os.path.join(d, "stations.tsv"), "w") as f:
            for i, (l, s, g) in enumerate(sts): f.write(f"{i}\t{l}\t{s}\t{g}\n")
        for i, (l, s, g) in enumerate(sts):
            open(os.path.join(d, f"report{i}.html"), "w").write(get(f"{BASE}/GetReport/{g}", {"allergens": "", "tags": ""}))
            time.sleep(1)
        # One nutrition label, to see what an item's full breakdown looks like
        r0 = open(os.path.join(d, "report0.html")).read()
        m = re.search(r"MenuItemClick\(this,\s*'[^']*',\s*'([^']+)',\s*'([^']+)'", r0)
        if m: open(os.path.join(d, "label.html"), "w").write(get(f"{BASE}/GetLabel/{m.group(1)}/{m.group(2)}", {"allergens": "", "tags": ""}))
        print(len(sts), "stations saved")
    else:
        out = sys.argv[1]
        rows = fetch_all()
        old = list(csv.reader(open(out, encoding="utf-8-sig")))[1:] if os.path.exists(out) else []
        problems = []
        if len(rows) < 800: problems.append(f"only {len(rows)} items")
        missing = {r[0] for r in old} - {r[0] for r in rows}
        if missing: problems.append("locations missing: " + ", ".join(sorted(missing)))
        key = lambda r: (r[0], r[1], r[3])
        gone = {key(r) for r in old} - {key(r) for r in rows}
        if old and len(gone) > 0.2 * len(old): problems.append(f"{len(gone)} of {len(old)} items would disappear")
        if problems:
            print("NOT updating the menu:", "; ".join(problems)); sys.exit(1)
        added = {key(r) for r in rows} - {key(r) for r in old}
        with open(out, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f); w.writerow(COLS); w.writerows(rows)
        print(f"{len(rows)} items ({len(added)} new, {len(gone)} gone)")
        for k in sorted(added)[:30]: print("  +", " / ".join(k))
        for k in sorted(gone)[:30]: print("  -", " / ".join(k))
