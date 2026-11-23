"""Season facts for The Over (daily trivia), computed from Cricsheet IPL match JSON.

Usage: python3 build_trivia.py <cricsheet_ipl_json_dir> <out_trivia.json>
Output: {year: {winner, runner, potm:[ids], final_xi:{team:[ids]}, venue, city, runs:[[id,runs]...top 6],
         wkts:[[id,wkts]...top 6], teams:[...]}}
"""
import collections, glob, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from build_stats import fr, SHORT, NOT_BOWLER_WICKETS

def main(src, out):
    runs = collections.defaultdict(collections.Counter); wk = collections.defaultdict(collections.Counter)
    S = collections.defaultdict(lambda: {"teams": set()})
    for f in glob.glob(os.path.join(src, "*.json")):
        d = json.load(open(f)); i = d["info"]; reg = i["registry"]["people"]; y = int(i["dates"][0][:4])
        tm = lambda t: SHORT.get(fr(t), fr(t))
        for t in i["players"]: S[y]["teams"].add(tm(t))
        for inn in d.get("innings", []):
            if inn.get("super_over"): continue
            for ov in inn.get("overs", []):
                for dl in ov["deliveries"]:
                    runs[y][reg[dl["batter"]]] += dl["runs"]["batter"]
                    for w in dl.get("wickets", []):
                        if w["kind"] not in NOT_BOWLER_WICKETS: wk[y][reg[dl["bowler"]]] += 1
        if i.get("event", {}).get("stage") == "Final" and "winner" in i.get("outcome", {}):
            w = i["outcome"]["winner"]; r = [t for t in i["teams"] if t != w][0]
            S[y].update(winner=tm(w), runner=tm(r), venue=i.get("venue", ""), city=i.get("city", ""),
                        potm=[reg[n] for n in i.get("player_of_match", [])],
                        final_xi={tm(t): [reg[n] for n in ps] for t, ps in i["players"].items()})
    outd = {}
    for y in sorted(S):
        s = S[y]; s["teams"] = sorted(s["teams"])
        s["runs"] = runs[y].most_common(6); s["wkts"] = wk[y].most_common(6)
        outd[y] = s
    json.dump(outd, open(out, "w"), separators=(",", ":"))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
