"""Build each player's IPL career path: the franchise he played for in each season, grouped into stints.

Usage: python3 build_paths.py <cricsheet_ipl_json_dir> <out_paths.json>
Output: {player_id: [[team, [seasons...]], ...]} in career order. A stint is a run of seasons for one
franchise with no other franchise in between (gap years stay in the same stint).
"""
import collections, glob, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from build_stats import fr, SHORT

def main(src, out):
    seasons = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))  # id -> year -> team -> matches
    first = {}
    for f in glob.glob(os.path.join(src, "*.json")):
        d = json.load(open(f)); i = d["info"]; reg = i["registry"]["people"]
        date = i["dates"][0]; year = int(date[:4])
        for team, plist in i["players"].items():
            for name in plist:
                pid = reg[name]; t = SHORT.get(fr(team), fr(team))
                seasons[pid][year][t] += 1
                k = (pid, year, t); first[k] = min(first.get(k, date), date)
    paths = {}
    for pid, by_year in seasons.items():
        seq = []
        for y in sorted(by_year):
            # the team(s) he played for that season, in the order he played for them
            for t in sorted(by_year[y], key=lambda t: first[(pid, y, t)]):
                seq.append((t, y))
        stints = []
        for t, y in seq:
            if stints and stints[-1][0] == t:
                if y not in stints[-1][1]: stints[-1][1].append(y)
            else:
                stints.append([t, [y]])
        paths[pid] = stints
    json.dump(paths, open(out, "w"), separators=(",", ":"))
    multi = sum(1 for s in paths.values() if len(s) >= 2)
    print(f"{len(paths)} players, {multi} with 2+ stints, longest path {max(len(s) for s in paths.values())} stints")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
