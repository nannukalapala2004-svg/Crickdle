"""Merge Cricsheet stats with curated names/countries and build the game page.

Usage: python3 build_site.py   (run from the project root)
Reads data/stats.json, data/meta.tsv, src/template.html
Writes data/players.json and index.html
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from roles import role  # noqa: E402

stats = json.load(open("data/stats.json"))
meta = {}
for line in open("data/meta.tsv", encoding="utf-8"):
    parts = line.rstrip("\n").split("\t")
    if len(parts) < 3:
        continue
    pid, name, country = parts[0], parts[1], parts[2]
    override = parts[3] if len(parts) > 3 else ""
    meta[pid] = (name, country, override)

missing = [k for k in stats if k not in meta]
if missing:
    sys.exit(f"meta.tsv is missing {len(missing)} players, e.g. {missing[:5]}")

# birth dates: verified file first, then curated (may be year-only); optional death date
born = {}
for fn in ("data/dob_verified.tsv", "data/dob_curated.tsv"):
    if not os.path.exists(fn):
        continue
    for line in open(fn, encoding="utf-8"):
        parts = line.rstrip("\n").split("\t")
        # rows flagged "?" are unconfirmed (year-only guesses): leave the age unknown
        if len(parts) >= 3 and parts[2] == "?":
            continue
        if len(parts) >= 2 and parts[0] not in born:
            born[parts[0]] = (parts[1], parts[3] if len(parts) > 3 else "")

rows = []
for pid, v in stats.items():
    name, country, override = meta[pid]
    rows.append([
        pid, name, " ".join(v["cs_names"]), country, override or role(v),
        v["last_team"], ",".join(v["teams"]), v["debut"], v["matches"],
        v["runs"], v["wkts"], v["titles"], v["last_season"],
        v["hs"] if v["innings"] else -1, 1 if v["hs_not_out"] else 0,
        v["bbi"][0] if v["bbi"] else -1, v["bbi"][1] if v["bbi"] else 0,
        born.get(pid, ("", ""))[0], born.get(pid, ("", ""))[1],
    ])
rows.sort(key=lambda r: (-r[8], r[1]))

# disambiguate identical display names
from collections import Counter
dup = Counter(r[1] for r in rows)
for r in rows:
    if dup[r[1]] > 1:
        r[1] = f"{r[1]} ({r[7]})"

with open("data/players.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, separators=(",", ":"))
data = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
html = open("src/template.html", encoding="utf-8").read().replace("/*__DATA__*/[]", data)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"{len(rows)} players, index.html {len(html)//1024} KB")
