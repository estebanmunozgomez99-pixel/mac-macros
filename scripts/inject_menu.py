"""Put data/build/data.json into app/index.html (as MENU_BUNDLED) and publish app/menu.json.

app/menu.json is what installed apps download to get menu changes without an app update: the same menu data
plus the SMPL rotation (ROTATIONS_BUNDLED in app/index.html), stamped with the build version."""
import json, re
data = open('data/build/data.json', encoding='utf-8').read()
s = open('app/index.html', encoding='utf-8').read()
a = s.index('const MENU_BUNDLED = '); b = s.index(';\n', a)
s = s[:a] + 'const MENU_BUNDLED = ' + data + s[b:]
open('app/index.html', 'w', encoding='utf-8').write(s)
rot = json.loads(re.search(r'^const ROTATIONS_BUNDLED = (.*);$', s, re.M).group(1))
menu = json.loads(data); menu['rotations'] = rot
open('app/menu.json', 'w', encoding='utf-8').write(json.dumps(menu, ensure_ascii=False, separators=(',', ':')))
print('app/index.html and app/menu.json updated')
