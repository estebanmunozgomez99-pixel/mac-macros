import pandas as pd, json, re
df=pd.read_csv('data/sources/mcmaster-menu-week.csv',encoding='utf-8-sig')
for c in ['Location','Station','Category','Menu Item','Serving Size']:
    df[c]=df[c].astype('string').str.strip()
def norm_serv(s):
    if pd.isna(s): return ''
    l=s.lower()
    if l in ('portion','portions','porion','piortion'): return 'Portion'
    return s[:1].upper()+s[1:].lower() if s.isalpha() else s
df['Serving Size']=df['Serving Size'].map(norm_serv)
est=4*df['Protein (g)']+4*df['Carbohydrate (g)']+9*df['Fat (g)']
ratio=est/df['Calories']
def flag(i):
    r=df.loc[i]
    if pd.isna(r['Calories']): return 'No nutrition info listed'
    if r['Calories']>5000: return 'Likely error in source data (calories far too high)'
    if r['Calories']>50 and ratio[i]>1.5: return 'Likely error in source data (macros do not add up)'
    return ''
df['Data Note']=[flag(i) for i in df.index]
df=df.sort_values(['Location','Station','Category','Menu Item'],kind='stable').reset_index(drop=True)
df.to_pickle('data/build/clean.pkl')
print(df['Data Note'].value_counts())
print(df['Serving Size'].value_counts())
