"""."""
import re
s = "dr. Boom -id=KAR_711 -faction=kara"

r1 = re.findall(r'-(.*?)=', s)
r2 = re.findall(r'-(.*?)(\s|-|$)', s)
print(r2)
args = {}
for x in r2:
    r1 = re.findall(r'(.*?)=', x[0])
    r3 = re.findall(r'=(.*?)$', x[0])
    s = s.replace("-" + x[0], "")
    args[r1[0]] = r3[0]
print(args)
print(s)
