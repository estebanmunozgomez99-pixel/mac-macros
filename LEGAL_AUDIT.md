# Maroon legal and compliance audit

Audit date: October 19, 2026. Scope: the app (`app/index.html`), the public pages at the site root, the build scripts and the data in this repo.

**This isn't legal advice.** Code changes lower risk; they can't remove it. Items marked **Lawyer** need a real answer from a lawyer. A university or law school legal clinic can be a low-cost place to start.

Laws considered (Canada/Ontario first):

- PIPEDA (privacy)
- Ontario's AODA, with WCAG 2.0 AA required and WCAG 2.2 AA targeted
- The Competition Act (misleading claims, drip pricing)
- CASL (commercial electronic messages)
- Ontario's Consumer Protection Act, 2002
- The Copyright Act and the Trademarks Act

## Summary table

| # | Item | Status | Why | What changed | Remaining risk / lawyer question |
|---|------|--------|-----|--------------|----------------------------------|
| 1 | Privacy policy | Applies | PIPEDA expects a plain-language account of personal information. Food logs and calculator details (age, sex, height, weight) are health-adjacent, even though they stay on the device. | Added `legal/privacy.md`, shown in the app (Settings → About and legal → Privacy Policy) and as a public `privacy.html`. It covers what's stored and where, no accounts/analytics/ads/selling, the third parties (GitHub Pages logs, Open Food Facts, the browser speech service, email), export/delete, children, changes, effective date and contact. | Low. If anything is ever sent to a server (accounts, sync, analytics, AI photo scanning), the policy and possibly consent flows must change first. |
| 2 | Terms of service | Applies | It sets expectations and limits liability for a free nutrition tool. | Added `legal/terms.md` (in the app and as `terms.html`). It covers: free; beta "as is"; not medical/dietary advice; third-party data may be wrong; allergens, ask staff; not affiliated; trademarks; acceptable use; limitation of liability with an Ontario consumer-law carve-out; under-13; changes; Ontario law; contact. | **Lawyer:** are the disclaimer and limitation clauses enforceable as written for Ontario consumers? Clickwrap vs browsewrap: the first-launch notice says "By using Maroon you agree", which is a weaker form of acceptance. |
| 3 | Refund policy | Doesn't apply | Nothing is sold. | The Terms say "Maroon is free and has no purchases, subscriptions, ads or in-app payments. There's nothing to refund." | If you add paid features, you'll need clear pricing before purchase, and the App Store/Play refund rules apply. |
| 4 | Cookie policy | Partly applies | There are no cookies, but localStorage is used, and it's fair to explain it. | Added a "Cookies and storage" section to the privacy policy: localStorage is used only to make the app work. | None. |
| 5 | Cookie consent banner | Doesn't apply (as a tracking banner) | All storage is strictly necessary for the app to work (your own log, goals, settings, offline menu copy), and there's no tracking, so there's nothing to consent to. A consent banner would imply tracking that doesn't exist. | Added a one-time first-launch notice: "Your food log stays on this device. By using Maroon you agree to the Terms and Privacy Policy." It has links and a **Got it** button, sits under any open sheet, and the acknowledgement is saved in the separate `maroon:prefs` key (`legalAck`, versioned as `LEGAL_VERSION`). Raising the version shows the notice again after a material change. | If the app is offered in the EU/UK, check the ePrivacy "strictly necessary" exemption (it should still apply). |
| 6 | Form consents | Doesn't apply | No form submits data anywhere. Search, goals, servings, the goal calculator, custom foods and Speak all stay in the browser. The only outbound inputs are a barcode number (to Open Food Facts) and the optional "Report a problem" email, which opens the user's own mail app. | Both are described in the privacy policy, and the CSP sets `form-action 'none'`. | The "Report a problem" email reaches the owner's inbox: replies only, no mailing list (see item 18). |
| 7 | No unnecessary data | Applies | Data minimisation is a PIPEDA principle. | Confirmed there are no analytics, location, device identifiers or fingerprinting. Speak keeps no audio or transcript: the text is matched right away and thrown away. The goal calculator details are optional and stored only so the form is filled in next time. | Low. You could add a "forget my calculator details" option; Delete all my data already covers it. |
| 8 | Third-party SDKs and requests | Applies | Every request to a third party can leak IP addresses. | **Requests the app makes:** (a) GitHub Pages (`estebanmunozgomez99-pixel.github.io`) for the app, `menu.json` and `hours.json`, which is the host itself; (b) Open Food Facts (`world.openfoodfacts.org`), only when a barcode is scanned or typed; (c) the browser's own speech service, only while Speak is listening. That one is made by the browser, not the page, so CSP doesn't cover it. **Figtree is self-hosted** (`app/vendor/fonts`), so there are no Google Fonts requests. The barcode reader (zxing-wasm) is bundled too. Added a Content-Security-Policy that limits `connect-src` to those two hosts, with `font-src 'self'`, `object-src 'none'`, `base-uri 'none'` and `form-action 'none'`. Verified that scanning, Open Food Facts lookups, menu updates and Speak still work with no CSP violations. The OFL text is in `legal/licenses.md`. | `script-src` has to allow `'unsafe-inline'` (single-file app) and `'wasm-unsafe-eval'` (barcode reader). If a hosting change ever allows HTTP headers, move the CSP to a header and add `frame-ancestors 'none'`. |
| 9 | Dark patterns | Applies | Competition Act, consumer protection and app store rules. | **Delete all my data** sits next to **Export my data** in Settings → Data: one tap plus a plain confirmation. There are no pre-checked boxes and no fake urgency. The score wording "Off target" became "Further from goal", and the help text says scores are "a rough guide, not a judgement". | The streak (kept at your request) is mild engagement pressure. It's neutral today: no loss messages and no notifications. Keep it that way. |
| 10 | Hidden fees | Doesn't apply | Nothing costs money. | "Free" is stated plainly in the Terms, the About page and the privacy policy. Nothing hints at future charges. | Drip pricing rules apply if you ever charge. |
| 11 | Fake reviews | Doesn't apply | There are no reviews, ratings, testimonials or user counts. | Nothing added. Rule recorded in CLAUDE.md: never add any unless they're real and confirmed. | Same rule for posters and Instagram (Competition Act). |
| 12 | Unsupported claims | Applies | Competition Act: general impression, superlatives, numbers. | The welcome copy no longer says "Every dining hall…". The High protein rule is shown on the tab: "At least 20 g of protein per 300 calories (and 5 g or more), best ratio first." Your data note is visible on Home and on the sample screen: "Nutrition info from McMaster Hospitality Services and restaurant-published guides. May not reflect recipe changes. Confirm allergens with staff." The goal calculator no longer predicts weight change ("500 cal below your estimate. Results vary") and points to a doctor or registered dietitian. Paramount's macros are labelled as estimates. | **Posters/Instagram:** see "Marketing wording" below. "The best way…" is a superlative you can't prove. |
| 13 | Alt text and screen readers | Applies | AODA / WCAG 1.1.1, 4.1.2. | The app has no `<img>` elements (icons are inline SVG). 29 decorative SVGs got `aria-hidden="true"`. Every icon-only button has an `aria-label`. Macro numbers in the log have spoken units ("32 protein"). The daily totals are announced politely through a hidden `aria-live` sentence instead of a noisy live region on the whole card. Sheet titles take focus when a sheet opens. The Progress chart has a text summary (`role="img"` label) and a "Show as a table" alternative (see Part 2). | Not tested with a real screen reader (VoiceOver/TalkBack). Worth a 10-minute check on your phone. |
| 14 | Colour contrast | Applies | WCAG 1.4.3 (text, 4.5:1) and 1.4.11 (UI, 3:1). | Added text-safe colour tokens and a two-tone focus ring. An automated scan of every text node in both themes found 1 failing pair before and 0 after. Before/after ratios are below. | The logo's gold on white (1.64:1) is exempt as a logo. Control borders are 1.39:1, but every control has a text label, so it isn't the only cue. |
| 15 | Keyboard navigation | Applies | WCAG 2.1.1, 2.1.2, 2.4.3, 2.4.7, 2.5.8, 1.4.10, 2.3.3. | Sheets trap Tab, close on Esc and return focus to the button that opened them; the page behind is `inert`. Closed sheets are hidden from Tab. "Choose a photo" labels work with Enter and Space. A visible maroon/gold focus ring with a contrasting gap. Touch targets are at least 44 px. `prefers-reduced-motion` turns off transitions, animations and smooth scrolling. No horizontal scrolling at 320 px width (equivalent to 200% zoom on a 640 px screen). | **Exceptions:** inline text links (WCAG exempts inline links), and the 7-across week strip and calendar days on Progress, which are about 34-36 px at 320 px wide (above the 24 px WCAG 2.2 AA minimum, below the 44 px goal; 44 px+ on most phones). |
| 16 | Business details | Applies | Ontario consumer law and app stores expect a way to identify and contact the maker. | Added an "About Maroon" page: student project by [OWNER NAME] in Hamilton, Ontario; contact email; app version; free; not affiliated; not advice; plus a "Data sources" page with every source and its date. | Fill in [OWNER NAME]. |
| 17 | Age and kids' data | Applies | Young users, and food tracking can affect people with eating disorders. | The Terms and privacy policy say Maroon is for university students and isn't directed at children under 13. Added a **Wellbeing** section in Settings, with contacts verified on the official sites on Oct 19, 2026: Student Wellness Centre 905-525-9140 ext. 27700 / wellness@mcmaster.ca; NEDIC 1-866-633-4220 (toll-free), 416-340-4156, live chat at nedic.ca; Good2Talk 1-866-925-5454 or text GOOD2TALKON to 686868 (24/7); "In an emergency, call 911." Going over a goal is shown in neutral colours, never red. A daily calorie goal under 1,200 shows a neutral note suggesting a doctor or registered dietitian, and saving is never blocked. | Phone numbers change: re-check them each term. **App stores:** a 4+ / Everyone age rating is likely, but answer the health questions honestly. |
| 18 | Unsubscribe links | Doesn't apply | Maroon sends no email. "Report a problem" only opens the user's own mail app, and replies to someone who wrote first aren't commercial messages. | Nothing added. | **CASL:** any future mailing list, newsletter or launch announcement needs express opt-in (no pre-checked box), your identity and contact details, and a working unsubscribe that's honoured within 10 business days. |
| 19 | Font, image and data licences | Applies | Copyright, trademark and licence terms. | Figtree (OFL), Lucide (ISC) and barcode-detector / zxing-wasm (MIT, with Apache-2.0 ZXing-C++) are credited with full texts in `legal/licenses.md`. **Horizon isn't used in the app**, and no Horizon files or licence are in the repo. The logo is original. No restaurant logos, no McMaster crest/logos/"Marauders" marks; restaurant names appear as plain text only. **The original restaurant PDFs and menu photos were removed from the repo** and are now kept in git-ignored `data/private/`; only extracted text stays public, and the build still works without the originals. Every data source is credited (licences page and Data sources page). Open Food Facts is credited under ODbL. | **Horizon:** find the licence from wherever you downloaded it. Free versions are often "personal use only", which wouldn't cover posters for a public app. Buy a commercial/desktop licence or switch fonts. **Lawyer:** reusing McMaster's nutrition site data and the restaurants' published nutrition numbers in a public app (facts aren't copyrightable in Canada, but compilations and the sites' terms of use can be). The "used with permission" from Hospitality Services is verbal: get it in writing (an email is fine). **The PDFs are still in git history** (you chose no history rewrite). Anyone can still download them from old commits; ask whether that matters, and if so, rewrite history and force-push. |
| 20 | Data deletion | Applies | PIPEDA access/correction, and app store rules require a deletion path. | Settings → Data: **Export my data** downloads a JSON file (log, goals, foods, calculator details, settings, prefs) and **Delete all my data** confirms, removes every `macmacros:*` and `maroon:*` key, and reloads the app. Restore from an exported file is also there. All three are explained in the privacy policy. | The browser can't delete copies the user made (exported files). |

## Contrast: before and after

Ratios are WCAG contrast ratios. AA needs 4.5:1 for normal text and 3:1 for large text and UI parts.

| Pair | Before | After |
|------|--------|-------|
| Light: text on background | 15.49 | 15.49 |
| Light: muted text on background | 5.09 | 5.09 |
| Light: muted on card | 5.62 | 5.62 |
| Light: muted on surface-2 (CLOSED tag) | 4.71 | 4.71 |
| Light: maroon link on card | 11.09 | 11.09 |
| Light: white on maroon | 11.09 | 11.09 |
| Light: gold on maroon | 6.74 | 6.74 |
| Light: #2B1A00 on gold (active tab) | 10.21 | 10.21 |
| Light: toast | 15.49 | 15.49 |
| Light: focus ring (gold on background) | **1.49 (fail)** | maroon ring 10.04, with white gap 11.09 |
| Light: carbs text (#E0A33A on white) | **2.22 (fail)** | #8A5A00: 5.93 on white, 5.36 on background, 4.97 on surface-2 |
| Light: fat text on white | 5.77 | 5.77 |
| Light: gold logo on white | 1.64 | 1.64 (logo, exempt) |
| Light: control border on card | 1.39 | 1.39 (controls have text labels) |
| Dark: text on background | 16.03 | 16.03 |
| Dark: muted on card | 6.44 | 6.44 |
| Dark: muted on surface-2 | 5.65 | 5.65 |
| Dark: gold link on card | 10.04 | 10.04 |
| Dark: protein text (#D9467F on card) | **4.04 (fail)** | #F07BA8: 6.37 on card, 7.08 on background |
| Dark: protein text on background | 4.48 (fail) | 7.08 |
| Dark: fat on card | 6.75 | 6.75 |
| Dark: toast | 16.03 | 16.03 |
| Dark: focus ring (gold on background) | 11.15 | 11.15 |
| Dark: search focus border (maroon on card) | **1.49 (fail)** | now uses the gold focus token (11.15) |

Bottom navigation and chart ratios are in the "Part 2" section below.

## Extra findings (not on the list)

1. **Restaurant PDFs are still in git history.** They're gone from the current files, but old commits on GitHub still contain them. Ask a lawyer whether this matters; if so, rewrite history (`git filter-repo`) and force-push.
2. **Your real email is public.** esteban.munoz.gomez99@gmail.com is in the app, the policies and the public pages, as you chose. Expect spam. A separate project address would be safer.
3. **Paramount estimates.** Paramount's protein, carbs and fat are estimated from posted menu-board calories. They're labelled "estimate" in the app and on the Data sources page. Keep that label wherever they appear (posters too).
4. **Goal calculator details** (sex, age, height, weight) are health-adjacent personal information. They stay on the device, are optional, are disclosed, and are erased by Delete all my data.
5. **"Report a problem" emails** go to your inbox. They contain the user's email address and what they wrote. Delete old ones you don't need, and never add them to a mailing list without opt-in (CASL).
6. **Open Food Facts data is ODbL.** It's credited. If you ever store or redistribute their data in bulk, ODbL share-alike applies.
7. **GitHub Pages server logs.** GitHub sees visitors' IP addresses. This is disclosed. GitHub is a US company; under PIPEDA, transfers outside Canada should be disclosed, and they are, by naming GitHub.
8. **The browser speech service** (Google or Apple) receives audio when Speak is used. This is disclosed. Maroon can't control it, so Speak only starts on tap.
9. **Allergen data.** The app deliberately doesn't present allergen information as reliable. Keep it that way. A wrong "nut-free" label is the biggest real-world harm risk in a food app.
10. **If you go outside Canada:** the EU/UK GDPR needs a lawful basis (likely "necessary for the service") and data-subject rights, which export/delete mostly cover. California's CCPA probably wouldn't apply at this size, but a "we don't sell data" line is already there.
11. **App Store / Google Play:**
    - Privacy "nutrition labels": "Data not collected" is accurate today.
    - Apple guideline 1.4.1 on health data accuracy: the disclaimers are already there.
    - Account deletion isn't needed because there are no accounts.
    - A support URL and privacy policy URL are needed: use `privacy.html` and the About page.
    - Apple guideline 5.1.1: microphone and camera purpose strings are needed in a native wrapper.
12. **Trademark use.** Restaurant names are used plainly to identify food (nominative use). Don't put brand logos, colours or slogans in posters. Say "Not affiliated with McMaster University or any restaurant" on marketing.
13. **The "Maroon" name** and McMaster's colours (maroon and gold). It's a common word and colour, but McMaster could object if marketing looks official. Keep the not-affiliated line and the original logo. **Lawyer:** is a trademark search worthwhile before an App Store launch?
14. **Focus rings use `:focus-visible`,** so keyboard users always see them and mouse or touch users don't get rings on every tap.

## Part 2: bottom navigation (re-checked after the change)

- **Structure:** `<nav aria-label="Main">` with Home / Progress / Settings buttons; the active one has `aria-current="page"`. The + button is `aria-label="Add food"` with `aria-expanded` and `aria-controls`. Its menu is a small modal (`role="dialog"`): it traps focus (+ and three options), closes on Esc or an outside tap, and returns focus to +. The page behind it is `inert` while it's open.
- **Speak:** the microphone is only requested after tapping Speak. Where the browser has no speech recognition, the option is replaced by a short explanation instead of a broken button. Matches are shown for confirmation, and nothing is logged until you tap Add. Audio and transcripts are never stored; this was verified by checking localStorage after a voice log. The privacy policy already describes this.
- **Scan:** the existing barcode scanner (your decision). No photo or AI scanning, so the privacy policy is unchanged.
- **Progress chart:** an inline SVG bar chart (no library) with a text summary for screen readers and a "Show as a table" alternative. Each day in the table is a 44 px button that opens the day on Home. The tone is neutral: averages and "X g of Y g" with no judgement words. The streak and scores stay (your decision).
- **Contrast checks:**
  - An automated scan of every text node on Home, the + menu, Add food, Settings, Progress (7 and 30 days, table open) and a document page, in both themes, found **0 failures**.
  - **Light theme:**
    - Active tab, maroon on white: 11.09.
    - Inactive tab, grey on white: 5.62.
    - The white + on maroon: 11.09. The + button against the page: 10.04.
    - Menu icons, maroon on surface-2: 9.30.
    - Chart bars: protein 11.09, carbs 5.93, fat 5.77 on white.
  - **Dark theme:**
    - Active tab, gold: 10.04.
    - Inactive tab: 6.44.
    - Menu icons: 8.82.
    - Chart bars: protein 6.37, carbs 10.04, fat 6.75. Axis labels: 6.44.
  - **One note:** in dark mode the maroon + circle is only 1.65:1 against the dark page. The white + symbol (11.09:1) is what identifies the button, so this meets WCAG 1.4.11. A lighter ring could be added if you want the circle itself to stand out more.
- **Touch targets and reflow:** all tabs, + and the menu options are 44 px or larger. The goal inputs went from 42 to 44 px. There's no horizontal scrolling at 320 px on any tab; the week strip was shrunk to fit.
- **Tested:**
  - At 390 px and 1280 px, in light and dark themes.
  - Keyboard only: tab order, the + menu trap, Esc, and focus returning after sheets.
  - No console errors in the app. The only errors were network requests this test machine blocks.
  - An existing `macmacros:v1` log loads with the same scores and streak as before.
  - All 17 regression scripts give the same results as the previous version. The only exception is the Progress page text, which now starts with the new chart.
