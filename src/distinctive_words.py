"""Helper: words that set each letter apart (tf-idf over data/wordindex.txt).

    python3 src/distinctive_words.py

Prints candidates per letter; the six shown on the page were picked by hand from this list
(see the `distinct` argument of each letter in build.py).
"""
import json, math
from paths import DATA

rows = {}
for part in (DATA / "wordindex.txt").read_text().split("|"):
    w, rest = part.split(":", 1)
    arr = [0] * 24
    for kv in rest.split(","):
        i, n = kv.split("."); arr[int(i)] = int(n)
    rows[w] = arr
tot = json.load(open(DATA / "totals.json"))["totals"]
boiler = set("zak nick letter letters partners partner partnership nomad inception fees fee annual interim percent index msci net performance results trailing year years period gross cumulative annualized basis thank sincerely yours housekeeping".split())
for i in range(24):
    sc = []
    for w, arr in rows.items():
        if w in boiler or arr[i] < 3: continue
        df = sum(1 for x in arr if x)
        sc.append((arr[i] / tot[i] * 1000 * math.log(24 / df), w, arr[i]))
    sc.sort(reverse=True)
    print(i, [f"{w}({n})" for s, w, n in sc[:12]])
