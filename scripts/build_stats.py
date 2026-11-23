"""Build per-player IPL stats from Cricsheet match JSON files.

Usage: python3 build_stats.py <cricsheet_ipl_json_dir> <out_stats.json>
"""
import collections
import glob
import json
import os
import sys

# Map historical franchise names to one current franchise label.
FRANCHISE = {
    "Delhi Daredevils": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
}
SHORT = {
    "Chennai Super Kings": "CSK",
    "Mumbai Indians": "MI",
    "Royal Challengers Bengaluru": "RCB",
    "Kolkata Knight Riders": "KKR",
    "Sunrisers Hyderabad": "SRH",
    "Rajasthan Royals": "RR",
    "Delhi Capitals": "DC",
    "Punjab Kings": "PBKS",
    "Lucknow Super Giants": "LSG",
    "Gujarat Titans": "GT",
    "Deccan Chargers": "DCH",
    "Pune Warriors": "PWI",
    "Gujarat Lions": "GL",
    "Rising Pune Supergiant": "RPS",
    "Kochi Tuskers Kerala": "KTK",
}
NOT_BOWLER_WICKETS = {"run out", "retired hurt", "retired out", "obstructing the field"}


def fr(team):
    return FRANCHISE.get(team, team)


def main(src, out):
    files = sorted(glob.glob(os.path.join(src, "*.json")))
    matches = []
    for f in files:
        with open(f) as fh:
            d = json.load(fh)
        matches.append(d)
    matches.sort(key=lambda d: d["info"]["dates"][0])

    P = collections.defaultdict(lambda: {
        "names": set(), "matches": 0, "seasons": set(), "teams": [], "last_team": None,
        "first_date": None, "last_date": None, "runs": 0, "balls": 0, "innings": 0,
        "outs": 0, "hs": 0, "fifties": 0, "hundreds": 0, "wkts": 0, "balls_bowled": 0,
        "runs_conceded": 0, "bowl_matches": 0, "catches": 0, "stumpings": 0,
        "bat_pos_sum": 0, "hs_no": False, "bbi": None, "titles": 0, "title_years": [], "potm": 0,
    })
    finals = 0
    for d in matches:
        i = d["info"]
        reg = i["registry"]["people"]
        date = i["dates"][0]
        year = int(date[:4])
        for team, plist in i["players"].items():
            for name in plist:
                p = P[reg[name]]
                p["names"].add(name)
                p["matches"] += 1
                p["seasons"].add(year)
                t = fr(team)
                if t not in p["teams"]:
                    p["teams"].append(t)
                p["last_team"] = t
                p["first_date"] = p["first_date"] or date
                p["last_date"] = date
        for name in i.get("player_of_match", []):
            P[reg[name]]["potm"] += 1
        # titles: winner of the final
        if i.get("event", {}).get("stage") == "Final" and "winner" in i.get("outcome", {}):
            finals += 1
            w = i["outcome"]["winner"]
            for name in i["players"][w]:
                P[reg[name]]["titles"] += 1
                P[reg[name]]["title_years"].append(year)

        # ball-by-ball
        bowled_in_match = set()
        for inn in d.get("innings", []):
            if inn.get("super_over"):
                continue
            order = []
            score = collections.Counter()
            dismissed = set()
            fig_w = collections.Counter()
            fig_r = collections.Counter()
            for ov in inn.get("overs", []):
                for dl in ov["deliveries"]:
                    for who in (dl["batter"], dl["non_striker"]):
                        if who not in order:
                            order.append(who)
                    ex = dl.get("extras", {})
                    b = reg[dl["batter"]]
                    bw = reg[dl["bowler"]]
                    P[b]["runs"] += dl["runs"]["batter"]
                    score[dl["batter"]] += dl["runs"]["batter"]
                    if "wides" not in ex:
                        P[b]["balls"] += 1
                    if "wides" not in ex and "noballs" not in ex:
                        P[bw]["balls_bowled"] += 1
                    conceded = dl["runs"]["batter"] + ex.get("wides", 0) + ex.get("noballs", 0)
                    P[bw]["runs_conceded"] += conceded
                    fig_r[bw] += conceded
                    bowled_in_match.add(bw)
                    for w in dl.get("wickets", []):
                        if w["player_out"] in order or True:
                            if w["player_out"] not in order:
                                order.append(w["player_out"])
                        if w["kind"] not in ("retired hurt",):
                            P[reg[w["player_out"]]]["outs"] += 1
                            dismissed.add(w["player_out"])
                        if w["kind"] not in NOT_BOWLER_WICKETS:
                            P[bw]["wkts"] += 1
                            fig_w[bw] += 1
                        for fl in w.get("fielders", []):
                            if fl.get("substitute") or "name" not in fl:
                                continue
                            if fl["name"] not in reg:
                                continue
                            fid = reg[fl["name"]]
                            if w["kind"] == "stumped":
                                P[fid]["stumpings"] += 1
                            elif w["kind"] in ("caught", "caught and bowled"):
                                P[fid]["catches"] += 1
                        if w["kind"] == "caught and bowled" and not w.get("fielders"):
                            P[bw]["catches"] += 1
            for pos, name in enumerate(order, 1):
                p = P[reg[name]]
                p["innings"] += 1
                p["bat_pos_sum"] += pos
                s = score[name]
                not_out = name not in dismissed
                if s > p["hs"] or (s == p["hs"] and not_out and not p["hs_no"]):
                    p["hs"], p["hs_no"] = s, not_out
                if s >= 100:
                    p["hundreds"] += 1
                elif s >= 50:
                    p["fifties"] += 1
            for bw in fig_r.keys() | fig_w.keys():
                fig = (fig_w[bw], fig_r[bw])
                best = P[bw]["bbi"]
                if best is None or fig[0] > best[0] or (fig[0] == best[0] and fig[1] < best[1]):
                    P[bw]["bbi"] = fig
        for bw in bowled_in_match:
            P[bw]["bowl_matches"] += 1

    res = {}
    for pid, p in P.items():
        res[pid] = {
            "id": pid,
            "cs_names": sorted(p["names"]),
            "matches": p["matches"],
            "debut": min(p["seasons"]),
            "last_season": max(p["seasons"]),
            "seasons": len(p["seasons"]),
            "teams": [SHORT[t] for t in p["teams"]],
            "last_team": SHORT[p["last_team"]],
            "runs": p["runs"],
            "balls": p["balls"],
            "innings": p["innings"],
            "hs": p["hs"],
            "hs_not_out": p["hs_no"],
            "bbi": list(p["bbi"]) if p["bbi"] else None,
            "fifties": p["fifties"],
            "hundreds": p["hundreds"],
            "avg_bat_pos": round(p["bat_pos_sum"] / p["innings"], 2) if p["innings"] else None,
            "wkts": p["wkts"],
            "balls_bowled": p["balls_bowled"],
            "runs_conceded": p["runs_conceded"],
            "bowl_matches": p["bowl_matches"],
            "catches": p["catches"],
            "stumpings": p["stumpings"],
            "titles": p["titles"],
            "title_years": p["title_years"],
            "potm": p["potm"],
        }
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)
    print(f"{len(matches)} matches, {finals} finals, {len(res)} players -> {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
