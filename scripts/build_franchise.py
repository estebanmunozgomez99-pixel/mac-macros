import json, re
out=[]
def add(loc,st,cat,item,serving,cal,fat,sat,chol,sod,carb,fib,sug,prot,kind,src):
    f=lambda v: None if v in (None,'') else float(str(v).replace('%',''))
    out.append(dict(location=loc,station=st,category=cat,item=item,serving=serving,calories=f(cal),fat=f(fat),satfat=f(sat),
        chol=f(chol),sodium=f(sod),carbs=f(carb),fibre=f(fib),sugars=f(sug),protein=f(prot),kind=kind,source=src))

# ---- Tim Hortons (MUSC): drinks and baked goods only
TIMS_SRC='Tim Hortons Canada Nutrition Information, August 2025'
KEEP={'Brewed Coffee':0,'Espresso Beverages':0,'Specialty Beverages':0,'Tea & Tea Lattes':0,'Iced Coffee & Cold Brew':0,'Iced Lattes':0,
      'Iced Capps':2,'Creamy Chills':2,'Lemonades':2,'Sparkling Quenchers':2,'Lemonade Quenchers':2,'Frozen Quenchers':2,
      'Dairy (single serving)':1,'Sugar (single serving)':1,'Flavoured Syrups (per pump)':1,
      'Donuts':2,'Timbits®':2,'Muffins':2,'Cookies & Brownies':2,'Croissants':2,'Tea Biscuits':2,'Savoury Pastries':2}
for r in json.load(open('data/build/tims.json')):
    g=r['grp']
    if g not in KEEP: continue
    name=r['name'].replace('Oragnge','Orange').replace('Cappuccino- ','Cappuccino - ').replace('Timbit ','Timbit').strip()
    if 'Quenchers' in g:
        kindword=g.split()[0]  # Sparkling / Lemonade / Frozen
        name=name.replace(' Quencher',f' {kindword} Quencher')
    cal,fat,sat,trans,chol,sod,carb,fib,sug,prot=r['vals']
    size=re.search(r' - (Small|Medium|Large|X Large|Regular)$',name)
    serving=size.group(1) if size else ('1 pump' if 'Syrup' in g else '1 item')
    cat=g.replace('®','')
    add('La Piazza','Tim Hortons',cat,name,serving,cal,fat,sat,chol,sod,carb,fib,sug,prot,KEEP[g],TIMS_SRC)

# ---- Second Cup (PG Centre and Bistro 2 Go): drinks
SC_SRC='Second Cup Beverage Menu Nutritional Values'
names=['Flat White','Caffé Latte','Vanilla Bean Latte','Caramel Corretto','Moccaccino','Cappuccino','Espresso','Americano',
 'Espresso Con Panna','Espresso Macchiato','Classic Hot Chocolate','White Hot Chocolate','Vanilla Bean Hot Chocolate','Coffee','Tea',
 'London Fog','Chai Latte','Honey Vanilla Tea Latte','Matcha Tea Latte','Espresso Frappé','Mocca Frappé','Caramel Frappé','Vanilla Bean Frappé',
 'Flash Cold Brew','Flash Cold Brew, Sweetened','Flash Cold Brew, Vanilla Bean','Flash Cold Brew, Mocca','Flash Cold Brew, Oat','Iced Americano',
 'Iced Caffè Latte','Iced Vanilla Bean Latte','Iced Moccaccino','Iced Caramel Corretto','Chai Frappé','Matcha Tea Frappé',
 'Brewed Iced Tea','Brewed Iced Tea, Sweetened','FroCho','Italian Soda','Strawberry Banana Glow Smoothie','Green Mango Boost Smoothie',
 'Almond Date Smoothie','Chocolate Banana Power Smoothie']
MILK={'2%':'2%','skim/écrémé':'skim','soy/soya':'soy','almond/amande':'almond','coconut/lait de coco':'coconut','oat/lait d’avoine':'oat','Oat/lait d’avoine':'oat','none/aucun':''}
blocks=json.load(open('data/build/sc.json')); assert len(blocks)==len(names)
def cat_for(n):
    if 'Frappé' in n or n in ('FroCho','Italian Soda') or 'Smoothie' in n: return 'Cold Bar'
    if n.startswith(('Iced','Flash','Brewed Iced')): return 'Cold Bar'
    if n in ('Coffee','Tea','London Fog','Chai Latte','Honey Vanilla Tea Latte','Matcha Tea Latte'): return 'Brew Bar'
    return 'Espresso Bar'
for n,b in zip(names,blocks):
    for v in b['rows']:
        milk=MILK.get(v[2].strip(),v[2].strip()); size=v[3].strip()
        item=f"{n} - {size}"+(f" ({milk})" if milk else '')
        cal,fat,sat,trans,carb,fib,sug,prot,chol,sod=v[4:14]
        for loc in ('PGCLL','Bistro 2 Go'):
            add(loc,'Second Cup',cat_for(n),item,size,cal,fat,sat,chol,sod,carb,fib,sug,prot,2,SC_SRC)

# ---- Chopped Leaf (PG Centre)
CL_SRC='Chopped Leaf Nutritional Chart'
sec=None; sub=''
num=r'-?\d+(?:\.\d+)?'
for line in open('data/build/cl.txt'):
    s=line.strip()
    if not s or s.startswith(('Nutritional Chart','Menu')): continue
    m=re.match(r'^(.*?)\s{2,}('+num+r'(?:\s+'+num+r'){6})$',s)
    if not m:
        if s in ('Multigrain','Sourdough'): sub=s
        else: sec=s; sub=''
        continue
    name=m.group(1).strip(); cal,fat,carb,fib,sug,prot,sod=m.group(2).split()
    if sec in ('Dressings','Proteins'): kind=1; item=('Extra ' if sec=='Proteins' else '')+name+(' (dressing)' if sec=='Dressings' and 'ressing' not in name and 'Sauce' not in name and 'Vinaigrette' not in name else '')
    elif sec in ('Chopped Water','Soups'): kind=2; item=name
    else:
        kind=0
        single={'Salads':'Salad','Bowls':'Bowl','Wraps':'Wrap','Quesadillas':'Quesadilla','Sandwiches':'Sandwich'}.get(sec)
        item=name if sec=='Kids Menu' else f"{name} {single}"+(f" ({sub})" if sub else '')
    if sec=='Chopped Water': item=f"Chopped Water, {name}"
    size=re.search(r' - (Small|Large)$',name)
    add('PGCLL','Chopped Leaf',sec,item,size.group(1) if size else '1 serving',cal,fat,None,None,sod,carb,fib,sug,prot,kind,CL_SRC)
# ---- Paramount Lebanese Kitchen (Centro)
# Calories are from the menu boards (photos in data/sources/paramount-*.jpg, Sept 28, 2026). Paramount publishes no
# protein/carb/fat numbers, so macros are estimates from typical portions, chosen so 4P + 4C + 9F ~= the posted calories.
# Build-your-own totals = posted base dish (e.g. the 940 Cal chicken meal minus the 170 Cal chicken) + posted protein.
PLK_SRC='Paramount menu boards at Centro, Sept 28, 2026. Calories as posted; protein, carbs and fat are estimates'
PLK_EST='Paramount menu boards at Centro, Sept 28, 2026. Base calories as posted; salad calories and all macros are estimates'
# name: (cal, protein, carbs, fat) for the protein portion, as posted
PROT={'Chicken Shawarma':(170,22,3,8),'Shish Tawouk':(280,30,4,16),'Falafel':(70,3,7,3.5),
      'Plant-Based Shawarma':(90,10,4,4),'Mushroom Shawarma':(90,3,8,5)}
def plk(cat,item,serving,cal,p,c,f,kind=0,src=PLK_SRC):
    add('Centro','Paramount Lebanese Kitchen',cat,item,serving,cal,f,None,None,None,c,None,None,p,kind,src)
# Wraps ($10.99): whole-wrap calories posted per wrap
for n,v in {'Chicken Shawarma':(1110,36,98,64),'Shish Tawouk':(1150,43,94,66),'Falafel':(1160,28,120,62),
            'Mushroom Shawarma':(1030,18,110,58),'Plant-Based Shawarma':(500,22,55,21)}.items():
    plk('Wraps',f'{n} Wrap','1 wrap',*v)
# Build your own: base dish + protein. Meal and salad boards list four proteins; the fries boards list all five.
BASES=[('Meal',' Meal','1 plate',(770,12,105,34),PROT.keys()-{'Mushroom Shawarma'},PLK_SRC),  # spicy potatoes, rice, salad
       ('Salad',' Salad','1 salad',(200,4,14,14),PROT.keys()-{'Mushroom Shawarma'},PLK_EST),
       ('Yalla Special',' Yalla Special Fries','1 plate',(1010,12,95,64),PROT.keys(),PLK_SRC),  # garlic and tahini sauce
       ('Poutine',' Poutine','1 plate',(882,22,90,48),PROT.keys(),PLK_SRC)]
for cat,suffix,serving,base,prots,src in BASES:
    for n in PROT:
        if n in prots: plk(cat,n+suffix,serving,*[b+x for b,x in zip(base,PROT[n])],src=src)
plk('Limited Time Offer','Beef Kafta Dinner','1 plate',950,30,106,44)
for n,v in PROT.items(): plk('Proteins',f'Extra {n}','1 portion',*v,kind=1)
json.dump(out,open('data/build/franchise.json','w'),ensure_ascii=False,indent=0)
from collections import Counter
print(len(out), Counter((o['location'],o['station'],o['kind']) for o in out))
print([o['item'] for o in out if o['station']=='Chopped Leaf'][::6])
print([o['item'] for o in out if o['station']=='Tim Hortons'][::15])
