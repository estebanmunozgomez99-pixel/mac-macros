# Mac Macros

A mobile-first macro tracker for McMaster University students (mainly first years). Students pick what they ate on campus and the app totals calories, protein, carbs and fat for the day.

## Layout

- `app/index.html` – the whole app: one self-contained HTML file (inline CSS and JS, no build step). Food data is embedded as `const MENU = {...}`. The daily log, goals and recent foods are saved in `localStorage` (key `macmacros:v1`), per device.
- `data/sources/` – original data: McMaster's menu export (CSV), official PDFs from Tim Hortons, Second Cup and Chopped Leaf (Chopped Leaf chart = their Oct 2025 Nutritionals & Allergens PDF), and photos of the Paramount menu boards at Centro.
- `scripts/` – Python that cleans the sources and regenerates the app data and spreadsheet.
- `build.sh` – runs the whole pipeline and rewrites the `MENU` block in `app/index.html`. Run it after any data or script change.
- `mcmaster-menu-nutrition.xlsx` – human-readable spreadsheet (About, Menu, Other Restaurants, By Location).

Requirements for the build: python3 with pandas, openpyxl, pdfplumber; `pdftotext` (poppler-utils).

## Hosting

- Live on GitHub Pages from `main` / root: https://estebanmunozgomez99-pixel.github.io/mac-macros/ (repo is public). Pushing to `main` updates the site in a minute or two.
- `index.html` at the root redirects to `app/`. `mac-macros/index.html` and `mac-macros/app/index.html` are redirects left from an early manual upload that nested everything under `mac-macros/`; keep them so old links and home-screen shortcuts work.
- The mic (voice logging) only works on https or localhost, so test voice on the live site.
- **Menu updates without an app update:** `build.sh` → `inject_menu.py` writes `const MENU_BUNDLED` into `app/index.html` and publishes `app/menu.json` (same data + `rotations`, stamped with `version` = build time UTC). The app uses the bundled copy unless a newer `menu.json` was downloaded earlier (`localStorage` `macmacros:menu`); it checks `MENU_URL` 3 s after opening and when returning after 6 h, and offers "Load it". `ROTATIONS = MENU.rotations || ROTATIONS_BUNDLED`. To ship a menu change: run `build.sh`, commit, push.
- **Nothing loads from other servers at runtime** (App Store rule): Figtree fonts and the barcode reader (barcode-detector + zxing wasm) are in `app/vendor/` (see its README). The ES-module reader can't load from `file://`; test scanning over http (e.g. `python3 -m http.server`).
- `privacy.html` (site root) is the privacy policy URL for the App Store. Contact email: esteban.munoz.gomez99@gmail.com (also `CONTACT_EMAIL` in `app/index.html`, used by Report a problem).

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
- **Settings (gear icon):** Appearance (Automatic / Light / Dark → `state.theme`, sets `data-theme` on `<html>`; a small script in `<head>` applies it before first paint), My foods (edit via the scan sheet's form, delete with `unregisterCustom`), backup (`exportBackup`: JSON file via share sheet or download; `importBackup` validates `app: "Mac Macros"` and replaces everything after a confirm), menu version + manual check, Report a problem / feedback, welcome tour, support resources (McMaster Student Wellness, NEDIC 1-866-633-4220, Good2Talk 1-866-925-5454), About (not affiliated, sources, not medical advice, privacy link, `APP_VERSION`).
- **Welcome sheet** on first open only (`state.onboarded`; existing saved data counts as onboarded): what the app does, disclaimer, Set my goals / Just explore.
- **Report a problem** link in every food picker: email to `CONTACT_EMAIL` with item details, or copies the report while no email is set. **Undo** after removing a logged meal.
- **Progress & daily score:** 📈 button next to the goals icon opens a Progress sheet: week strip (score rings, ‹ › weeks, avg + ▲/▼ vs previous week, on-target streak), month calendar shaded by score (see bands below; blank = nothing logged; tap a day to open it), and month stats (days on target, calories within 10%, protein goal hit, average day). Score (`dayScore`/`partScore`): calories 40 pts, protein 30, carbs 15, fat 15. Each part: full marks in the perfect zone (calories ±3%, protein ≥ goal, carbs/fat ±5%), sliding to 93% at the guideline edge (±10% calories, 90% of protein goal, ±15% carbs/fat), then a curve down to 0 at ±40% calories / half the protein goal / ±50% carbs and fat. So 100 = nailed it, 93-99 = inside the guidelines. Bands (`ON_TARGET`, `CLOSE`): 95+ on target (maroon), 85-94 close (gold), 84 and under off (grey), plus not logged; streak and "days on target" count 95+. Unset goals are left out and the rest scaled to 100; unlogged days have no score. Each day is scored against the goals it was logged under (`state.dayGoals`, pinned when food is added and before goals change). No calorie goal: nudge to the calculator plus averages only. The summary card shows a "Today 82 · On target" chip that opens Progress. Protein over goal isn't flagged as "over".
- **Make it a meal:** a main's picker shows "Make it a meal" chips with the sides from its own station's extras (`mealSides`): side-dish categories (Carb Sides, Plant Based Sides, Salads, Sides, All Day, Brunch, Breakfast, Entrée) whose names look like sides (`SIDE_NAME`), plus fries/onion rings/hash browns/tater tots from Add Ons; swaps ("Sub …") excluded; breakfast/brunch sides only on breakfast mains; Centro SMPL only today's rotation sides. Tap once for a side, twice for a double. Totals and nutrition facts include them, and Add to log saves them as the entry's extras (editable later). Not shown on build-your-own items that open a builder.
- **Nutrition facts:** "Nutrition facts" toggle in the Add food picker, an ⓘ button on each logged item (includes extras), and a small ⓘ in the top-right corner of the summary card for the whole day. % Daily Value uses Health Canada values (`FACTS` in `app/index.html`). Unpublished nutrients show "—"; day totals missing some items get a * note. Log entries store `micro`; older entries are looked up by id.
- Search ignores accents (`fold`).
- **Goal calculator:** "Calculate my goals →" under the Daily goals fields opens a sheet (sex, age, height, weight in metric or imperial, activity, priority). Maintenance = Mifflin-St Jeor × activity factor; plans: Lose fat −500 (floor 1,500 male / 1,200 female), Maintain, Build muscle +250, Gain weight +500; protein 2.0/1.6/1.8/1.6 g per kg; fat 25% of calories; carbs the rest. "Use this as my goal" sets all four goals. Inputs are saved in `state.profile`.
- The High protein tab label has a 💪.
- **Build-your-own engine:** `BUILDERS` in `app/index.html` (step kinds: one / qty / toggle / share / amount). Rows appear at the top of the builder's station and when searching (`searchQ`). Adding saves the build to My foods ("Built by you") and logs it.
- **Omelette build your own:** "🍳 Build your own omelette" at Centro Pas Noodle and LAH Morning & Mains (builders can list several `places`). 2/3/4 eggs (McMaster "One Egg" 85 cal), meats (Pas Noodle numbers at 50 g / 2 bacon slices / half chicken portion), Pas Noodle veggies, cheddar 30 g, side: toast (McMaster "Two Eggs & Toast" − 2 eggs = 269 cal), hashbrown (190) or none; cooking oil/butter 120 cal is an estimate always included. Default build 800 cal vs McMaster's BYO Omelette 831.
- **Bistro omelette bar builder (The Bistro @ MKR, Breakfast Classics):** eggs, fillings (McMaster Bistro toppings: bacon, chorizo, spinach, mushrooms, red peppers, red onion, avocado), cheddar blend / feta, side: home fries & toast (= McMaster "Bistro Breakfast - Bacon" − 2 eggs − 3 bacon slices = 536 cal), toast only, or none; + estimated cooking fat. Typical build 1,087-1,227 cal vs McMaster's 1,174.
- **Flavour Junction builder (LAH The Flavour Hub):** style (Fiesta Fare / Shawarma / Mediterranean / Thai One) + protein = McMaster's official meal used as-is (`fjMeal` reads it from the menu; only combos McMaster makes are offered). Extras on top: extra protein (McMaster per-100 g/portion numbers), sides (pita, udon, fries, spring mix) and extra base, whose portions are estimates (≈). Step options can be functions of the build (`stepOpts`).
- **Customize buttons:** menu items that are really build-your-own (`CUSTOMIZE` in `app/index.html`: "Build Your Own Pasta", "Build Your Own Omelette", "Eggsactly Your Omelette") show "Customize ingredients →" in place of Add to log, opening the builder (they can't be logged as-is). Full meals (Flavour Junction combos) keep Add to log and get "Customize: add extras →", which opens the builder preset to that style + protein.
- **Names:** `appdata3.py` rewrites "Byo" to "Build Your Own" in McMaster item names; "Centro Byo Two Protein Pasta" is dropped (`DROP_ITEMS`) since the builder covers it.
- **Pas Noodle build your own (Centro):** "🍝 Build your own pasta": pasta, sauce (two share a portion) + Light/Regular/Extra, proteins, veggies, cheese. All ingredient numbers are McMaster's own (listed per 100 g); portions are calibrated so McMaster's published BYO totals match (80 g dry pasta, 100 g sauce, 100 g protein or 1 chicken portion, 40 g per veggie, 20 g cheddar, pesto 30 g, rosé = 1 portion, bacon = 2 slices): one protein 631 vs 633 cal, two 921 vs 928. `PAS` is generated from `clean.pkl` (see the git history for the script); regenerate if McMaster's Pas Noodle add-ons change.
- **Chopped Leaf build your own:** a "🥗 Build your own" row at the top of the Chopped Leaf list (PGCLL and Eco Bean) (and when searching build/byo/chopped) opens a builder sheet: Salad/Bowl/Wrap, greens, grain, proteins (steppers, up to ×3), toppings (tap once/twice for extra), dressings (two dressings share one portion) and Light/Regular/Extra. Live totals at the top. Adding saves it to My foods ("Built by you") and logs it. Data in `BYO` in `app/index.html`: proteins/dressings = official chart; rice (200 cal, 36 C, 3 P) and tortilla (250 cal, 6 F, 46 C, 8 P, 390 mg Na) derived from the official salad vs bowl vs wrap differences; greens/toppings = USDA estimates at typical portions (marked ≈). Rebuilding the signature bowls from parts lands within ~5-10% of the official totals.
- **Barcode scanning / My foods:** barcode button next to Add food and in the search bar opens a scanner sheet (live camera, "Use a photo", or typing the number). Uses the browser's `BarcodeDetector` when it supports EAN/UPC (Android Chrome), otherwise loads `barcode-detector@3.2.2` (zxing-wasm) from jsDelivr on first use. Looks up Open Food Facts (`world.openfoodfacts.org/api/v2/product/<code>.json`, free, no key; `fromOFF` converts per-serving or per-100 g values, sodium etc. g→mg). Confirm card: servings stepper or grams eaten. Not found → "Enter it yourself" form (also used to edit). Saved foods live in `state.custom` on the phone and are registered into the menu as location "My foods" (stations "Scanned" / "Added by you") so search, Recent, voice and High protein see them.
- **Voice logging:** 🎤 next to Add food and in the search bar (only shown where the browser has speech recognition; needs https). Enter in the search box only closes the keyboard (normal search results stay); when a multi-word search finds nothing, a "Log it as a sentence instead" button runs the same matcher on the typed text (card says "You typed"). `parseSpoken` in `app/index.html` splits the sentence into items (commas, "plus", "and" before a count), reads place nicknames (`PLACES`: Tims, Booster, BTG, …), size, milk and count, then fuzzy-matches names (`scoreGroup`: rare words weigh more, typos allowed). Nothing is logged automatically: each match shows as a card with Size/Milk/servings buttons, "Not it?" alternatives, and Add / Add all. A size or milk the drink doesn't have is flagged ("No oat milk for this one"). No AI service; an AI parser (behind a small server holding the API key) was discussed as a later option.
- **High protein type tabs:** on the High protein tab the gold row shows food types instead (Drinks, Sandwiches & Wraps, Bowls & Salads, Mains, Fish, Pasta & Noodles, Soups, Snacks), from `FOOD_TYPES` rules on the item name and category in `app/index.html`.
- **High protein tab:** item qualifies if protein/calories ≥ 2/30 (20 g per 300 kcal) and protein ≥ 5 g. Sorted by best ratio. Extras excluded.
- Tim Hortons at La Piazza sells **drinks and baked goods only** (no sandwiches, soups or bagels). Plain coffee, tea and lattes are meals so they can take cream/milk/sugar/syrup extras.

## Locations for non-McMaster restaurants

- La Piazza → Tim Hortons, Booster Juice
- DBAC (David Braley Athletic Centre) → Booster Juice
- PGCLL → Second Cup, Chopped Leaf (full menu)
- Eco Bean - MUMC → Chopped Leaf ("powered by Chopped Leaf": everything except soups and Chopped Water), plus its own McMaster Breakfast station
- Bistro 2 Go → Second Cup
- Centro → Paramount Lebanese Kitchen (wraps, build-your-own meal/salad/Yalla Special fries/poutine, Beef Kafta Dinner LTO; proteins are extras)
- There is no "MUSC" location; the user said MUSC isn't a place in the app.

## Known data caveats

- Several McMaster items list a "100g" serving while the numbers are clearly for the whole item. Kept as posted.
- Two unlabeled blocks in the Second Cup PDF are named Espresso and Americano from their position on the menu.
- Paramount Lebanese Kitchen publishes calories only. Macros are estimates (user approved), salad calories too. Build-your-own = posted base dish + posted protein calories. Recheck if Paramount releases a nutrition guide.
- Booster Juice data is Booster Juice's own in-store Nutrition Guide v24.1, typed from the user's photos into `data/sources/booster-juice-nutrition-guide-v24.1.tsv` (photos: `booster-juice-guide-v24.1-*.jpg`). It includes calcium and iron (mg), which go into the franchise micro array. `Booster-Juice-Menu-2023.pdf` (calories only) is kept for reference.
- Starbucks PDFs the user found were the Ireland/Northern Ireland menu, so Starbucks was not added.

## To-do

- Before the App Store: McMaster Hospitality permission for their data (user is asking) then wrap with Capacitor (bundle `app/`), Apple developer account, TestFlight beta.

- Starbucks: needs the Canadian nutrition guide (starbucks.ca).
- Teriyaki Experience (student centre): not started.
- Later: native iOS/Android version (React Native/Expo was the suggested route) for sharing with all first years.

## Style

- Colours: McMaster maroon `#7A003C`, gold `#FDBF57`; light and dark themes via CSS tokens.
- Font: Figtree (Google Fonts) with system fallbacks.
- Keep the app a single HTML file unless the user asks otherwise.
