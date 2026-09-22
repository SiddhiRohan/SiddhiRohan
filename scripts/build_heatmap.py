"""Render assets/contributions.svg from the GitHub contribution calendar."""
import json, os, urllib.request
from datetime import date

USER = "SiddhiRohan"
Q = '{ user(login:"%s"){ contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } } } } }' % USER
req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": Q}).encode(),
    headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "User-Agent": "profile-readme"})
cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
weeks, total = cal["weeks"], cal["totalContributions"]

BG, EMPTY, TEXT = "#0b1218", "#151d26", "#8b949e"
SCALE = ["#1b3a3f", "#1f6f6b", "#2ec4b6", "#f5a623"]      # teal ramp, amber for the busiest days
counts = sorted(c["contributionCount"] for w in weeks for c in w["contributionDays"] if c["contributionCount"])
def color(n):
    if n == 0: return EMPTY
    q = lambda p: counts[min(int(len(counts) * p), len(counts) - 1)]
    if n >= q(0.9): return SCALE[3]
    if n >= q(0.6): return SCALE[2]
    if n >= q(0.3): return SCALE[1]
    return SCALE[0]

CELL, GAP, L, T = 14, 4, 40, 34
W = L + len(weeks) * (CELL + GAP) + 20
H = T + 7 * (CELL + GAP) + 40
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="11">',
       f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>']
last_month = None
for wi, w in enumerate(weeks):
    for c in w["contributionDays"]:
        d = date.fromisoformat(c["date"])
        x = L + wi * (CELL + GAP); y = T + d.isoweekday() % 7 * (CELL + GAP)
        if d.strftime("%b") != last_month and d.day <= 7:
            last_month = d.strftime("%b")
            out.append(f'<text x="{x}" y="{T-10}" fill="{TEXT}">{last_month}</text>')
        out.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{color(c["contributionCount"])}"><title>{c["date"]}: {c["contributionCount"]}</title></rect>')
for lbl, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
    out.append(f'<text x="{L-8}" y="{T + row*(CELL+GAP) + 11}" fill="{TEXT}" text-anchor="end">{lbl}</text>')
fy = H - 14
out.append(f'<text x="{L}" y="{fy}" fill="{TEXT}">{total} contributions in the last year</text>')
lx = W - 20 - 4 * (CELL + GAP) - 40
out.append(f'<text x="{lx-6}" y="{fy}" fill="{TEXT}" text-anchor="end">less</text>')
for i, col in enumerate([EMPTY] + SCALE[:3]):
    out.append(f'<rect x="{lx + i*(CELL+GAP)}" y="{fy-11}" width="{CELL}" height="{CELL}" rx="3" fill="{col}"/>')
out.append(f'<text x="{lx + 4*(CELL+GAP)}" y="{fy}" fill="{TEXT}">more</text>')
out.append("</svg>")
open("assets/contributions.svg", "w", encoding="utf-8", newline="\n").write("\n".join(out))
print("wrote heatmap:", total, "contributions,", len(weeks), "weeks")
