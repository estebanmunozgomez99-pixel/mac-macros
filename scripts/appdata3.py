import pandas as pd, json, re
df=pd.read_pickle('data/build/clean.pkl'); df=df[df['Data Note']==''].copy()
EXTRA_CATS={'Add Ons','Toppings','Sides','Carb Sides','Plant Based Sides','Build Its'}
KEEP_MAIN={'St Classic Poutine'}
SIDE_NAMES={'centro brown spanish rice','centro jasmine rice','market vegetables','mashed potatoes','naan',
            'lo mein noodles','homefries','centro garlic bread','garlic bread with cheese','scrambled egg','one egg',
            'bacon','turkey bacon','gravy'}
extra_pat=re.compile(r'^(add|side|sub|sublah|extra fruit)\b|\bside\b|\bside hashbrown$',re.I)
def is_extra(r):
    n=r['Menu Item']; l=n.lower()
    if n in KEEP_MAIN: return False
    if r['Category'] in EXTRA_CATS: return True
    if l in SIDE_NAMES or extra_pat.search(n): return True
    if l.endswith('fries') and len(l.split())<=3 and '&' not in l: return True
    return False
NONMEAL_CATS={'Dessert','Beverage','Cups'}
nonmeal_pat=re.compile(r'parfait|yogu?rt|smoothie|milkshake|matcha|latte|coffee|\btea\b|juice|lemonade|ice cream|sundae|(chocolate|cheese|carrot|coffee|pound|lava|red velvet|velvet) cake|cake pop|cookie|brownie|muffin|pudding|crumble|brulee|mousse|acai|mango banana|nutella|honey bee|wow butter|\bscoops?\b|donut|(oatmeal|granola|protein|energy|nanaimo|date|krispie) bar|fruit cup|trail mix|guacamole and chips',re.I)
def kind(r):
    if is_extra(r): return 1
    if r['Category'] in NONMEAL_CATS or nonmeal_pat.search(r['Menu Item']): return 2
    return 0
df['kind']=df.apply(kind,axis=1)
def nice_station(s): return s.title() if s.isupper() and len(s)>4 else s
def nice_name(s): return re.sub(r'^(Lp|Smpl|Sub Smpl|Sub Lp|Sub)\s+',lambda m: 'Sub ' if m.group(1).startswith('Sub') else '',s).strip()
df['st']=df['Station'].map(nice_station); df['nm']=df['Menu Item'].map(nice_name)
# SMPL stations: savory mains first (meat, fish, plant-based, pasta, other), desserts last
CAT_RANK={'Meat Based Entrees':0,'FISH DISHES':1,'Plant Based Entrees':2,'Pasta':3,'All Day':4,'Other':5}
def rank(r):
    if 'smpl' not in r['Station'].lower(): return 0
    return (100 if r['kind']==2 else 0) + CAT_RANK.get(r['Category'],50)
df['rank']=df.apply(rank,axis=1)
df=df.sort_values(['Location','st','rank'],kind='stable')
FR=json.load(open('data/build/franchise.json'))
# Category tabs in the app: tidy names, and merge small categories into a few tabs per restaurant
CAT_MERGE={
 'Tim Hortons':{'Brewed Coffee':'Hot Drinks','Espresso Beverages':'Hot Drinks','Specialty Beverages':'Hot Drinks','Tea & Tea Lattes':'Hot Drinks',
   'Iced Coffee & Cold Brew':'Iced Coffee','Iced Lattes':'Iced Coffee','Iced Capps':'Iced Coffee',
   'Creamy Chills':'Cold Drinks','Lemonades':'Cold Drinks','Sparkling Quenchers':'Cold Drinks','Lemonade Quenchers':'Cold Drinks','Frozen Quenchers':'Cold Drinks',
   'Muffins':'Baked Goods','Cookies & Brownies':'Baked Goods','Croissants':'Baked Goods','Tea Biscuits':'Baked Goods','Savoury Pastries':'Baked Goods'},
 'Booster Juice':{'Fresh Juices':'Juices','Specialty':'Bowls, Shots & Snacks','Grilled Fresh':'Food'},
 'Chopped Leaf':{'Chopped Water':'Drinks'},
 'Bakery Items':{'Breakfast':'Bagels, Muffins & Croissants'},'Baked Goods':{'Breakfast':'Bagels, Muffins & Croissants'},
 'All Day Menu':{'All Day':'Burgers & Poutine'},
}
CAT_NAMES={'~None':'Other','FISH DISHES':'Fish','Meat Based Entrees':'Meat','Plant Based Entrees':'Plant-Based','Dessert':'Desserts','All Day Menu':'All Day','Sandwich':'Sandwiches'}
def cat_name(station,c):
    c=str(c or '').strip()
    return CAT_MERGE.get(station,{}).get(c) or CAT_NAMES.get(c,c)
cats=[]
def cat_index(station,c):
    n=cat_name(station,c)
    if n not in cats: cats.append(n)
    return cats.index(n)
locs=sorted(set(df['Location'].unique())|{r['location'] for r in FR}); stations=[]; rows=[]; seen=set()
for _,r in df.iterrows():
    key=(r['Location'],r['st'])
    if key not in stations: stations.append(key)
    vals=[round(float(r[c]),1) for c in ['Calories','Protein (g)','Carbohydrate (g)','Fat (g)']]
    vals=[int(v) if v==int(v) else v for v in vals]
    k=(r['Location'],r['st'],r['nm'],r['Serving Size'],*vals)
    if k in seen: continue
    seen.add(k); rows.append([stations.index(key),r['nm'],r['Serving Size'],*vals,int(r['kind']),cat_index(r['st'],r['Category'])])
# Non-McMaster restaurants (Tim Hortons, Second Cup, Chopped Leaf)
for r in FR:
    if r['calories'] is None: continue
    key=(r['location'],r['station'])
    if key not in stations: stations.append(key)
    vals=[round(float(r[c] or 0),1) for c in ['calories','protein','carbs','fat']]
    vals=[int(v) if v==int(v) else v for v in vals]
    k=(r['location'],r['station'],r['item'],r['serving'],*vals)
    if k in seen: continue
    seen.add(k); rows.append([stations.index(key),r['item'],r['serving'],*vals,r['kind'],cat_index(r['station'],r['category'])])
out={'locations':locs,'stations':[[locs.index(l),s] for l,s in stations],'categories':cats,'items':rows}
open('data/build/data.json','w').write(json.dumps(out,ensure_ascii=False,separators=(',',':')))
from collections import Counter
print(Counter(r[7] for r in rows))
# report: stations with extras -> meals that can take extras vs not
by={}
for r in rows: by.setdefault(r[0],[]).append(r)
for si,rs in by.items():
    if any(r[7]==1 for r in rs):
        print('##',out['stations'][si][1],'| non-meal:',[r[1] for r in rs if r[7]==2][:12],'| new extras:',[r[1] for r in rs if r[7]==1][:40])
