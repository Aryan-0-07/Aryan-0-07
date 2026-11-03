import json
import math
import os
import sys
import urllib.request

USER = os.environ.get("GH_USER", "Aryan-0-07")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = os.environ.get("OUT_FILE", "languages.svg")
MOCK = os.environ.get("MOCK_LANGS")

COLORS = ["#C084FC", "#9333EA", "#E879F9", "#7E22CE", "#A5B4FC", "#F0ABFC"]


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-langs"})
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def collect():
    if MOCK:
        return json.loads(MOCK)
    totals = {}
    repos = get("https://api.github.com/users/%s/repos?per_page=100&type=owner" % USER)
    for repo in repos:
        if repo.get("fork"):
            continue
        for lang, n in get(repo["languages_url"]).items():
            totals[lang] = totals.get(lang, 0) + n
    return totals


def build(totals):
    items = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:5]
    if not items:
        items = [("No data yet", 1)]
    total = sum(n for _, n in items)
    cx, cy, ro, ri = 95, 110, 70, 44
    parts = []
    angle = -math.pi / 2
    for i, (name, n) in enumerate(items):
        frac = n / total
        sweep = frac * 2 * math.pi
        color = COLORS[i % len(COLORS)]
        if frac > 0.9999:
            parts.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="%d"/>' % (cx, cy, (ro + ri) / 2, color, ro - ri))
        else:
            a2 = angle + sweep
            r = (ro + ri) / 2
            x1, y1 = cx + r * math.cos(angle), cy + r * math.sin(angle)
            x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
            large = 1 if sweep > math.pi else 0
            parts.append('<path d="M%.2f %.2f A%d %d 0 %d 1 %.2f %.2f" fill="none" stroke="%s" stroke-width="%d"/>' % (x1, y1, r, r, large, x2, y2, color, ro - ri))
        angle += sweep
    legend = []
    for i, (name, n) in enumerate(items):
        y = 70 + i * 28
        pct = n / total * 100
        color = COLORS[i % len(COLORS)]
        legend.append('<rect x="205" y="%d" width="12" height="12" rx="3" fill="%s"/>' % (y - 10, color))
        legend.append('<text x="226" y="%d" font-size="14" fill="#E9D5FF">%s</text>' % (y, name.replace("&", "&amp;")))
        legend.append('<text x="395" y="%d" font-size="14" fill="#C084FC" text-anchor="end">%.0f%%</text>' % (y, pct))
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="420" height="220" viewBox="0 0 420 220" font-family="Verdana, Geneva, sans-serif">'
        '<rect width="420" height="220" rx="12" fill="#0d1117" stroke="#4c1d95"/>'
        '<text x="24" y="32" font-size="16" font-weight="700" fill="#C084FC">Top languages</text>'
        + "".join(parts)
        + '<text x="%d" y="%d" font-size="12" fill="#AFA9EC" text-anchor="middle">%d langs</text>' % (cx, cy + 4, len(items))
        + "".join(legend)
        + '<text x="24" y="208" font-size="11" fill="#7F77DD">Based on public repos</text></svg>'
    )


if __name__ == "__main__":
    try:
        svg = build(collect())
    except Exception as e:
        print("failed:", e, file=sys.stderr)
        sys.exit(1)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", OUT)
