"""Replace CSS light-dark(a, b) with plain variables so dark mode works in older browsers.
Light values go in :root, dark values in :root[data-theme=dark] and (when no theme is chosen) the
prefers-color-scheme: dark media query."""
import re, sys

def split_args(s, start):
    # s[start] is just after "light-dark(" ; return (a, b, end_index_after_close_paren)
    depth, i, comma = 0, start, None
    while True:
        c = s[i]
        if c == "(":
            depth += 1
        elif c == ")":
            if depth == 0: break
            depth -= 1
        elif c == "," and depth == 0 and comma is None:
            comma = i
        i += 1
    return s[start:comma].strip(), s[comma + 1:i].strip(), i + 1

def fix(path):
    s = open(path, encoding="utf-8").read()
    a, b = s.index("<style>"), s.index("</style>")
    css = s[a:b]
    light, dark, n = [], [], 0
    out, i = "", 0
    # 1) inside the :root{...} block, "--x:light-dark(a,b)" becomes "--x:a" plus a dark override
    while True:
        j = css.find("light-dark(", i)
        if j < 0: out += css[i:]; break
        A, B, end = split_args(css, j + len("light-dark("))
        m = re.search(r"(--[\w-]+):\s*$", css[:j])
        if m:   # a variable definition
            var = m.group(1); out += css[i:j] + A; dark.append(f"{var}:{B}")
        else:   # used directly in a rule: give it its own variable
            n += 1; var = f"--ld{n}"; light.append(f"{var}:{A}"); dark.append(f"{var}:{B}"); out += css[i:j] + f"var({var})"
        i = end
    block = ""
    if light: block += ":root{" + ";".join(light) + "}\n"
    if dark:
        d = ";".join(dark)
        block += f":root[data-theme=dark]{{{d}}}\n@media(prefers-color-scheme:dark){{:root:not([data-theme=light]){{{d}}}}}\n"
    out = out.replace("</style>", "") + "\n/* dark mode values (plain variables, no light-dark(), so older browsers work) */\n" + block
    s = s[:a] + out + s[b:]
    open(path, "w", encoding="utf-8").write(s)
    print(path, "vars:", len(dark), "inline:", n, "left:", s.count("light-dark("))

for p in sys.argv[1:]:
    fix(p)
