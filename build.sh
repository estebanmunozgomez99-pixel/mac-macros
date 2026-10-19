#!/usr/bin/env bash
# Rebuild everything from data/sources. Run from the project root.
# Needs: python3 with pandas and openpyxl (plus pdfplumber and pdftotext only to refresh extracts from data/private/ PDFs).
set -e
python3 scripts/clean.py
# Restaurant PDFs aren't published in the repo (only their extracted numbers are, in data/extracted/).
# If you have the original PDFs, put them in data/private/ (git-ignored) and the extracts are refreshed from them.
P=data/private; X=data/extracted
if [ -f $P/Tim-Hortons-Nutrition-Guide.pdf ]; then pdftotext -layout $P/Tim-Hortons-Nutrition-Guide.pdf $X/tims-hortons-guide.txt; fi
if [ -f $P/Chopped-Leaf-Nutritional-Chart.pdf ]; then pdftotext -layout $P/Chopped-Leaf-Nutritional-Chart.pdf $X/chopped-leaf-chart.txt; fi
if [ -f $P/Second-Cup-Nutritional-Facts-BL.pdf ]; then python3 scripts/sc.py > /dev/null && cp data/build/sc.json $X/second-cup.json; fi
cp $X/tims-hortons-guide.txt data/build/tims.txt
cp $X/chopped-leaf-chart.txt data/build/cl.txt
cp $X/second-cup.json data/build/sc.json
python3 scripts/tims.py
python3 scripts/build_franchise.py > /dev/null
python3 scripts/appdata3.py > /dev/null
python3 scripts/inject_menu.py
python3 scripts/build_xlsx.py
python3 scripts/build_legal.py
