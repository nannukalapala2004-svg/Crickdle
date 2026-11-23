def role(v):
    m = v["matches"]
    if v["stumpings"] >= 2 or (v["stumpings"] >= 1 and m <= 25):
        return "WK"
    share = v["bowl_matches"] / m
    rpm = v["runs"] / m
    pos = v["avg_bat_pos"] or 11
    if share >= 0.4:
        return "AR" if (rpm >= 8 and pos <= 7) else "BOWL"
    return "BAT"
