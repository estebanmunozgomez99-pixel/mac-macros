"""Replace the MENU data block inside app/index.html with data/build/data.json."""
s = open('app/index.html', encoding='utf-8').read()
a = s.index('const MENU = '); b = s.index(';\n', a)
s = s[:a] + 'const MENU = ' + open('data/build/data.json', encoding='utf-8').read() + s[b:]
open('app/index.html', 'w', encoding='utf-8').write(s)
print('app/index.html updated')
