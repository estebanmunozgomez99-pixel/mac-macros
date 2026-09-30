"""Download McMaster's menu from macnutrition.mcmaster.ca (the site McMaster Hospitality said we can use).

The page is an ASP.NET DevExpress app: /Nutrition/ServiceMenuReport/Today lists locations and stations; each
station has a GUID (packed in the navUnits control's base64 'itemsInfo', in the same order as the rendered
station links), and POSTing to /Nutrition/ServiceMenuReport/GetReport/<guid> returns that station's items.

  python3 scripts/fetch_macnutrition.py --raw DIR   save the raw pages (for working out the report format)
"""
import base64, html, http.cookiejar, os, re, sys, time, urllib.parse, urllib.request

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
