#!/usr/bin/env bash
# Rebuild everything from data/sources. Run from the project root.
# Needs: python3 with pandas, openpyxl, pdfplumber; and pdftotext (poppler-utils).
set -e
python3 scripts/clean.py
pdftotext -layout data/sources/Tim-Hortons-Nutrition-Guide.pdf data/build/tims.txt
pdftotext -layout data/sources/Chopped-Leaf-Nutritional-Chart.pdf data/build/cl.txt
python3 scripts/tims.py
python3 scripts/sc.py > /dev/null
python3 scripts/build_franchise.py > /dev/null
python3 scripts/appdata3.py > /dev/null
python3 scripts/inject_menu.py
python3 scripts/build_xlsx.py
