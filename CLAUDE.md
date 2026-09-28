# Mac Macros

A mobile-first macro tracker for McMaster University students (mainly first years). Students pick what they ate on campus and the app totals calories, protein, carbs and fat for the day.

## Layout

- `app/index.html` – the whole app: one self-contained HTML file (inline CSS and JS, no build step). Food data is embedded as `const MENU = {...}`. The daily log, goals and recent foods are saved in `localStorage` (key `macmacros:v1`), per device.
- `data/sources/` – original data: McMaster's menu export (CSV) and official PDFs from Tim Hortons, Second Cup and Chopped Leaf.
- `scripts/` – Python that cleans the sources and regenerates the app data and spreadsheet.
- `build.sh` – runs the whole pipeline and rewrites the `MENU` block in `app/index.html`. Run it after any data or script change.
- `mcmaster-menu-nutrition.xlsx` – human-readable spreadsheet (About, Menu, Other Restaurants, By Location).

Requirements for the build: python3 with pandas, openpyxl, pdfplumber; `pdftotext` (poppler-utils).

## Data pipeline

1. `clean.py` – cleans McMaster's CSV: merges misspelled serving sizes, adds a `Data Note` flag for rows with blank nutrition or obviously wrong numbers (over 5,000 kcal, or macros not adding up). Flagged rows are kept in the spreadsheet but left out of the app.
2. `tims.py`, `sc.py` – parse the Tim Hortons and Second Cup PDFs. Chopped Leaf is parsed inside `build_franchise.py` from `pdftotext -layout` output.
3. `build_franchise.py` – builds non-McMaster rows and assigns them to campus locations.
4. `appdata3.py` – builds `data/build/data.json` (the `MENU` object) and classifies every item.
5. `inject_menu.py` – writes `MENU` into `app/index.html`.
6. `build_xlsx.py` – builds the spreadsheet.

`MENU` format: `locations` (names), `stations` (`[locationIndex, name]`), `items` (`[stationIndex, item, serving, calories, protein, carbs, fat, kind]`).

`kind`: `0` = meal (can take extras), `1` = extra/add-on (only shown inside Edit on a logged meal), `2` = snack, dessert or drink (logged normally, no extras). Classification rules are in `appdata3.py` (`is_extra`, `kind`) and `build_franchise.py`.

## Product rules the user asked for (keep these)

- **Extras** (add-ons, toppings, sauces, sides) never appear in the main food list. They're added via the Edit button on a logged meal.
- Extras only work on **real meals** (not parfaits, desserts, drinks), and only extras from the **same station/restaurant** as the meal. Fruit toppings only on waffles, pancakes, French toast.
- **SMPL stations:** savory mains first (meat, fish, plant-based, pasta, other), desserts last.
- **Daily SMPL rotation (Centro only):** Centro SMPL runs a 4-week Monday–Sunday cycle from hospitality.mcmaster.ca. The schedule is in `ROTATIONS` in `app/index.html`; dishes not on the schedule are hidden except desserts and "Sub" swaps. There's a "Show all weeks" toggle. **Open question:** `week1Monday` is set to `2026-09-07` as a guess (makes Mon Sept 28, 2026 = Week 4). The user was going to confirm by checking what's on the Centro SMPL line. LAH SMPL and Bistro SMPL have no published daily schedule yet.
- **High protein tab:** item qualifies if protein/calories ≥ 2/30 (20 g per 300 kcal) and protein ≥ 5 g. Sorted by best ratio. Extras excluded.
- Tim Hortons at La Piazza sells **drinks and baked goods only** (no sandwiches, soups or bagels). Plain coffee, tea and lattes are meals so they can take cream/milk/sugar/syrup extras.

## Locations for non-McMaster restaurants

- La Piazza → Tim Hortons
- PGCLL → Second Cup, Chopped Leaf
- Bistro 2 Go → Second Cup
- There is no "MUSC" location; the user said MUSC isn't a place in the app.

## Known data caveats

- Several McMaster items list a "100g" serving while the numbers are clearly for the whole item. Kept as posted.
- Two unlabeled blocks in the Second Cup PDF are named Espresso and Americano from their position on the menu.
- Starbucks PDFs the user found were the Ireland/Northern Ireland menu, so Starbucks was not added.

## To-do

- Booster Juice (MUSC location and ByMac at the David Bradley Athletic Centre): needs official nutrition data.
- Starbucks: needs the Canadian nutrition guide (starbucks.ca).
- Teriyaki Experience (student centre): not started.
- Confirm the Centro SMPL week (see above).
- Later: native iOS/Android version (React Native/Expo was the suggested route) for sharing with all first years.

## Style

- Colours: McMaster maroon `#7A003C`, gold `#FDBF57`; light and dark themes via CSS tokens.
- Font: Figtree (Google Fonts) with system fallbacks.
- Keep the app a single HTML file unless the user asks otherwise.
