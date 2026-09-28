import pdfplumber, json, re, bisect
pdf=pdfplumber.open('data/sources/Second-Cup-Nutritional-Facts-BL.pdf'); p=pdf.pages[0]
edges=sorted(set(round(e['top']) for e in p.edges if e['orientation']=='h' and e['x0']<200<e['x1']))
edges=[e for e in edges if e>=294]
t=p.find_tables()[1]; data=t.extract()
rows=[]
for r,vals in zip(t.rows,data):
    tops=[c[1] for c in r.cells if c]; bots=[c[3] for c in r.cells if c]
    if not vals or vals[3] is None or not re.search(r'\d',vals[4] or ''): continue
    rows.append(dict(top=min(tops),bot=max(bots),vals=vals))
# labels in name column
def label_between(y0,y1):
    cs=[c for c in p.chars if 150<c['x0']<370 and y0<=c['top']<y1 and c['text'].strip()!='' or (150<c['x0']<370 and y0<=c['top']<y1 and c['text']==' ')]
    up=[c for c in cs if c.get('upright')]
    rot=[c for c in cs if not c.get('upright')]
    # only take name-column text: exclude type column (x>=300 upright tokens are milk types)
    up=[c for c in up if c['x0']<300]
    out=[]
    if up:
        from collections import defaultdict
        L=defaultdict(list)
        for c in up: L[round(c['top'])].append(c)
        out+= [''.join(c['text'] for c in sorted(L[k],key=lambda c:c['x0'])) for k in sorted(L)]
    if rot:
        from collections import defaultdict
        X=defaultdict(list)
        for c in rot: X[round(c['x0']/6)].append(c)
        out+= [''.join(c['text'] for c in sorted(X[k],key=lambda c:-c['top'])) for k in sorted(X)]
    return ' '.join(s.strip() for s in out if s.strip())
blocks=[]
for a,b in zip(edges,edges[1:]):
    rs=[r for r in rows if a-2<=r['top']<b-2]
    if rs: blocks.append(dict(label=label_between(a,b),rows=rs))
for i,bl in enumerate(blocks): print(i,len(bl['rows']), repr(bl['label'][:40]))
json.dump([dict(label=b['label'],rows=[r['vals'] for r in b['rows']]) for b in blocks],open('data/build/sc.json','w'),ensure_ascii=False)
print(sum(len(b['rows']) for b in blocks), len(rows))
