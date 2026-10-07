"""Hours of operation from McMaster Hospitality's "What's Open Now" page (hospitality.mcmaster.ca/maceats/open-now/),
which loads a LibCal feed. Writes app/hours.json, a small file the app downloads on its own (separate from the menu,
so new hours never show a "menu update" prompt).

  python3 scripts/fetch_hours.py [FEED.json]   (reads a saved feed instead of downloading, for testing)

app/hours.json: {"updated": ISO time, "source": ..., "hours": {KEY: {"YYYY-MM-DD": [[open, close], ...] | "closed" | "24h"}}}
where KEY is an app location ("Centro") or "Location|Station" ("La Piazza (MUSC)|Starbucks"), and open/close are
minutes after midnight (close can pass 1440 for after-midnight closing). A station without its own key uses its location's.
"""
import datetime, json, re, sys, urllib.request

FEED = "https://hospitality-mcmaster.libcal.com/widget/hours/grid?iid=4258&format=json&weeks=2&systemTime=0"
UA = "Mozilla/5.0 (Maroon campus macro app hours updater; contact esteban.munoz.gomez99@gmail.com)"
# LibCal name -> app location (display name) or "Location|Station". Unlisted LibCal places aren't in the app.
MAP = {
    "Bistro @ MKR": "The Bistro @ MKR",
    "Bistro-2-Go (MKR)": "Bistro 2 Go",
    "Café One (MDCL)": "Café One",
    "Centro (Commons)": "Centro",
    "Ecobean (HSC)": "Eco Bean - MUMC",
    "IAHS Café": "IAHS Café",
    "La Piazza (MUSC)": "La Piazza (MUSC)",
    "Booster Juice (MUSC)": "La Piazza (MUSC)|Booster Juice",
    "Starbucks (MUSC)": "La Piazza (MUSC)|Starbucks",
    "Tim Hortons (MUSC)": "La Piazza (MUSC)|Tim Hortons",
    "LAH": "Lincoln Alexander Hall",
    "Chopped Leaf (PGCLL)": "PGCLL|Chopped Leaf",
    "Second Cup (PGCLL)": "PGCLL|Second Cup",
    "Reactor Café (Thode)": "Reactor Café and Lounge",
    "Refuelling Station (DBAC)": "DBAC",  # the DBAC spot that serves Booster Juice
}

def minutes(t):
    """'7:30am' / '11pm' / '12am' -> minutes after midnight."""
    m = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?\s*([ap])m", t.strip().lower())
    if not m: raise ValueError(f"time {t!r}")
    h = int(m.group(1)) % 12 + (12 if m.group(3) == "p" else 0)
    return h * 60 + int(m.group(2) or 0)

def day_hours(times):
    st = times.get("status")
    if st == "closed": return "closed"
    if st == "24hours": return "24h"
    if st != "open": raise ValueError(f"status {st!r}")
    out = []
    for r in times.get("hours", []):
        a, b = minutes(r["from"]), minutes(r["to"])
        if b <= a: b += 1440  # closes after midnight
        out.append([a, b])
    return out or "closed"

def build(feed):
    hours, unknown = {}, []
    for loc in feed["locations"]:
        key = MAP.get(loc["name"])
        if not key: unknown.append(loc["name"]); continue
        days = hours.setdefault(key, {})
        for week in loc["weeks"]:
            for v in week.values(): days[v["date"]] = day_hours(v.get("times", {}))
    missing = set(MAP) - {l["name"] for l in feed["locations"]}
    return hours, unknown, missing

if __name__ == "__main__":
    if len(sys.argv) > 1: feed = json.load(open(sys.argv[1]))
    else:
        with urllib.request.urlopen(urllib.request.Request(FEED, headers={"User-Agent": UA}), timeout=60) as r: feed = json.load(r)
    hours, unknown, missing = build(feed)
    if len(hours) < 8: sys.exit(f"Only {len(hours)} places in the hours feed; not updating app/hours.json")
    out = {"updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "source": "McMaster Hospitality hours (hospitality.mcmaster.ca/maceats/open-now)", "hours": hours}
    try: old = json.load(open("app/hours.json"))
    except Exception: old = {}
    if old.get("hours") == hours: print("hours unchanged"); sys.exit(0)
    json.dump(out, open("app/hours.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"hours updated: {len(hours)} places", "| not in app:", ", ".join(unknown), "| missing from feed:", ", ".join(missing) or "none")
