# Mac Macros

A mobile-first macro tracker for McMaster University students (mainly first years). Students pick what they ate on campus and the app totals calories, protein, carbs and fat for the day.

## Layout

- `app/index.html` – the whole app: one self-contained HTML file (inline CSS and JS, no build step). Food data is embedded as `const MENU = {...}`. The daily log, goals and recent foods are saved in `localStorage` (key `macmacros:v1`), per device.
- `data/sources/` – original data: McMaster's menu export (CSV), official PDFs from Tim Hortons, Second Cup and Chopped Leaf, and photos of the Paramount menu boards at Centro.
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

`MENU` format: `locations` (names), `stations` (`[locationIndex, name]`), `categories` (names), `items` (`[stationIndex, item, serving, calories, protein, carbs, fat, kind, categoryIndex, nutrients]`), where nutrients = `[sat fat g, cholesterol mg, sodium mg, fibre g, sugars g, vitamin C mg, calcium mg, iron mg]` with `null` where the source doesn't publish it (vitamins/minerals are McMaster-only; Chopped Leaf lacks sat fat/cholesterol; Paramount has none). Category names are tidied/merged in `appdata3.py` (`CAT_MERGE` per station, `CAT_NAMES`).

`kind`: `0` = meal (can take extras), `1` = extra/add-on (only shown inside Edit on a logged meal), `2` = snack, dessert or drink (logged normally, no extras). Classification rules are in `appdata3.py` (`is_extra`, `kind`) and `build_franchise.py`.

## Product rules the user asked for (keep these)

- **Extras** (add-ons, toppings, sauces, sides) never appear in the main food list. They're added via the Edit button on a logged meal.
- Extras only work on **real meals** (not parfaits, desserts, drinks), and only extras from the **same station/restaurant** as the meal. Fruit toppings only on waffles, pancakes, French toast.
- **SMPL stations:** savory mains first (meat, fish, plant-based, pasta, other), desserts last.
- **Daily SMPL rotation (Centro only):** Centro SMPL runs a 4-week Monday–Sunday cycle from hospitality.mcmaster.ca. The schedule is in `ROTATIONS` in `app/index.html`; dishes not on the schedule are hidden except desserts and "Sub" swaps. There's a "Show all weeks" toggle. `week1Monday` is `2026-09-28`: confirmed from a photo of the Centro SMPL board on Mon Sept 28, 2026, which matched Week 1 Monday exactly (Honey Balsamic Basa, Roasted Pesto Chicken, Beef & Lentil Shepherd's Pie, Veg Tikka Masala, Zucchini/Peppers/Tomato, Vegetable Rice Pilaf). LAH SMPL and Bistro SMPL have no published daily schedule yet.
- **One row per drink:** sizes and milks of the same drink are grouped into one row in the Add food list (e.g. Second Cup "Caffé Latte"); tapping it shows Size and Milk buttons. Grouping happens in the app (`GROUPS` in `app/index.html`) from the item names: "Name - <size> (<milk>)" where size is Small/Medium/Large/X Large/Regular/Single/Double or N oz/mL, plus La Piazza bowls ending in "Small". Only items with a size/milk are grouped; the log keeps the full variant name. Recent reopens on the size/milk logged last; the High protein tab shows a drink if any size qualifies.
- **Category tabs:** when a station is picked and it shows 40+ items (`CAT_TABS_MIN`) in more than one category, a gold tab row (Everything, Soups, Donuts, …) filters the list. Counted on what's served that day, ignoring the search box.
- **Nutrition facts:** "Nutrition facts" toggle in the Add food picker, an ⓘ button on each logged item (includes extras), and a small ⓘ in the top-right corner of the summary card for the whole day. % Daily Value uses Health Canada values (`FACTS` in `app/index.html`). Unpublished nutrients show "—"; day totals missing some items get a * note. Log entries store `micro`; older entries are looked up by id.
- Search ignores accents (`fold`).
- **Goal calculator:** "Calculate my goals →" under the Daily goals fields opens a sheet (sex, age, height, weight in metric or imperial, activity, priority). Maintenance = Mifflin-St Jeor × activity factor; plans: Lose fat −500 (floor 1,500 male / 1,200 female), Maintain, Build muscle +250, Gain weight +500; protein 2.0/1.6/1.8/1.6 g per kg; fat 25% of calories; carbs the rest. "Use this as my goal" sets all four goals. Inputs are saved in `state.profile`.
- The High protein tab label has a 💪.
- **High protein type tabs:** on the High protein tab the gold row shows food types instead (Drinks, Sandwiches & Wraps, Bowls & Salads, Mains, Fish, Pasta & Noodles, Soups, Snacks), from `FOOD_TYPES` rules on the item name and category in `app/index.html`.
- **High protein tab:** item qualifies if protein/calories ≥ 2/30 (20 g per 300 kcal) and protein ≥ 5 g. Sorted by best ratio. Extras excluded.
- Tim Hortons at La Piazza sells **drinks and baked goods only** (no sandwiches, soups or bagels). Plain coffee, tea and lattes are meals so they can take cream/milk/sugar/syrup extras.

## Locations for non-McMaster restaurants

- La Piazza → Tim Hortons, Booster Juice
- DBAC (David Braley Athletic Centre) → Booster Juice
- PGCLL → Second Cup, Chopped Leaf
- Bistro 2 Go → Second Cup
- Centro → Paramount Lebanese Kitchen (wraps, build-your-own meal/salad/Yalla Special fries/poutine, Beef Kafta Dinner LTO; proteins are extras)
- There is no "MUSC" location; the user said MUSC isn't a place in the app.

## Known data caveats

- Several McMaster items list a "100g" serving while the numbers are clearly for the whole item. Kept as posted.
- Two unlabeled blocks in the Second Cup PDF are named Espresso and Americano from their position on the menu.
- Paramount Lebanese Kitchen publishes calories only. Macros are estimates (user approved), salad calories too. Build-your-own = posted base dish + posted protein calories. Recheck if Paramount releases a nutrition guide.
- Booster Juice data is Nutritionix's Booster Juice menu (`data/sources/booster-juice-nutritionix.tsv`, pasted by the user). "<5"/"<1" values are entered as 0. `Booster-Juice-Menu-2023.pdf` (calories only) is kept for reference.
- Starbucks PDFs the user found were the Ireland/Northern Ireland menu, so Starbucks was not added.

## To-do

- Starbucks: needs the Canadian nutrition guide (starbucks.ca).
- Teriyaki Experience (student centre): not started.
- Later: native iOS/Android version (React Native/Expo was the suggested route) for sharing with all first years.

## Style

- Colours: McMaster maroon `#7A003C`, gold `#FDBF57`; light and dark themes via CSS tokens.
- Font: Figtree (Google Fonts) with system fallbacks.
- Keep the app a single HTML file unless the user asks otherwise.
