import re, json
num=r'-?\d+(?:\.\d+)?'
rx=re.compile(r'^\s*(\S.*?)\s{2,}('+num+r')'+(r'\s+('+num+r')')*9+r'\s*$')
rows=[]; sec=None; grp=None
skip=('Protein','Sugars','Total Sugars','Calories','Saturated','Cholesterol','Carbohydrates','Sodium','Trans Fat','Menu Item','Fibre','Fat (g)','©','Tot','Total','Nutrition Information','The nutrition','nutritional software','suppliers,','Test,','products served','This document')
for line in open('data/build/tims.txt'):
    if not line.strip() or line.startswith('\f') and not line.strip('\f').strip(): continue
    l=line.strip('\f').rstrip()
    m=rx.match(l)
    if m:
        vals=re.findall(num,l[m.start(2):])
        rows.append(dict(sec=sec,grp=grp,name=m.group(1).strip(),vals=[float(v) for v in vals]))
    else:
        s=l.strip()
        if not s or s.startswith(skip) or len(s)<3: continue
        if s in ('Coffee, Tea & Other Hot Beverages','Cold Beverages','Beverage Additions','Baked Goods','Breakfast','Lunch','Breakfast - Limited Time Only','Lunch - Limited Time Only'): sec=s; grp=None
        else: grp=s
json.dump(rows,open('data/build/tims.json','w'))
from collections import Counter
print(len(rows)); print(Counter((r['sec'],r['grp']) for r in rows))
print([r for r in rows if len(r['vals'])!=10][:3])
