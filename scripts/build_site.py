"""Merge Cricsheet stats with curated names/countries and build the game page.

Usage: python3 build_site.py   (run from the project root)
Reads data/stats.json, data/meta.tsv, src/template.html
Writes data/players.json, player/index.html (the game) and index.html (the home page)
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
# Iconic players mode: names listed in data/iconic.txt
by_name = {r[1]: r[0] for r in rows}
iconic = [l.strip() for l in open("data/iconic.txt", encoding="utf-8") if l.strip() and not l.startswith("#")]
missing = [n for n in iconic if n not in by_name]
if missing:
    raise SystemExit(f"data/iconic.txt names not found in players: {missing}")
html = open("src/template.html", encoding="utf-8").read().replace("/*__DATA__*/[]", data).replace("/*__ICONIC__*/[]", json.dumps([by_name[n] for n in iconic]))
import os, shutil
# Career Path game: players + their season-by-season franchise paths (data/paths.json from build_paths.py)
paths = json.load(open("data/paths.json", encoding="utf-8"))
icon_ids = {by_name[n] for n in iconic}
cp_players = [[r[0], r[1], r[2], r[3], r[4], r[8], r[9], r[10], r[7], r[12]] for r in rows if r[0] in icon_ids]
cp = open("src/path.html", encoding="utf-8").read()
cp = cp.replace("/*__PATHDATA__*/{players:[], paths:{}}", json.dumps({"players": cp_players, "paths": paths}, ensure_ascii=False, separators=(",", ":")))
cp = cp.replace("/*__FLAGS__*/{}", open("data/flags.json", encoding="utf-8").read())
cp = cp.replace("/*__ICONIC__*/[]", json.dumps([by_name[n] for n in iconic]))
# The Over (daily trivia): players, paths and season facts (data/trivia.json from build_trivia.py)
ov_players = [[r[0], r[1], r[3], r[8], r[9], r[10], r[7], r[12], r[13], r[14]] for r in rows]
ov = open("src/over.html", encoding="utf-8").read()
ov = ov.replace("/*__OVERDATA__*/{players:[], paths:{}, seasons:{}}", json.dumps({"players": ov_players, "paths": paths, "seasons": json.load(open("data/trivia.json", encoding="utf-8"))}, ensure_ascii=False, separators=(",", ":")))
ov = ov.replace("/*__FLAGS__*/{}", open("data/flags.json", encoding="utf-8").read())
os.makedirs("over", exist_ok=True)
with open("over/index.html", "w", encoding="utf-8") as f:
    f.write(ov)
os.makedirs("path", exist_ok=True)
with open("path/index.html", "w", encoding="utf-8") as f:
    f.write(cp)
os.makedirs("player", exist_ok=True)
with open("player/index.html", "w", encoding="utf-8") as f:
    f.write(html)
shutil.copyfile("src/home.html", "index.html")
shutil.copyfile("src/account.js", "account.js")   # shared account panel (code, always refreshed)
if not os.path.exists("config.js"):   # keep your own settings once created
    shutil.copyfile("src/config.js", "config.js")
print(f"{len(rows)} players, player/index.html {len(html)//1024} KB, home page index.html")
