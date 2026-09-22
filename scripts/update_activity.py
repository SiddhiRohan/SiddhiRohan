"""Fill the activity block in README.md from the public GitHub events feed."""
import json, os, re, urllib.request
from datetime import datetime, timezone

USER = "SiddhiRohan"
MAX_LINES = 5
START, END = "<!--START_SECTION:activity-->", "<!--END_SECTION:activity-->"

req = urllib.request.Request(
    f"https://api.github.com/users/{USER}/events/public?per_page=100",
    headers={"User-Agent": "profile-readme", "Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN','')}"},
)
events = json.load(urllib.request.urlopen(req))

def age(ts):
    d = datetime.now(timezone.utc) - datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if d.days >= 30: return f"{d.days // 30}mo ago"
    if d.days >= 1: return f"{d.days}d ago"
    return f"{max(d.seconds // 3600, 1)}h ago"

lines, seen = [], set()
for e in events:
    repo = e["repo"]["name"]
    if repo == f"{USER}/{USER}": continue          # skip this repo's own refresh commits
    url = f"https://github.com/{repo}"
    t = e["type"]; p = e["payload"]
    if t == "PushEvent" and p.get("head"):
        try:
            c = json.load(urllib.request.urlopen(urllib.request.Request(
                f"https://api.github.com/repos/{repo}/commits/{p['head']}", headers=req.headers)))
            msg = c["commit"]["message"].splitlines()[0]
        except Exception:
            msg = p["head"][:7]
        line = f"Pushed to [{repo}]({url}): *{msg}*"
    elif t == "PullRequestEvent":
        pr = p["pull_request"]; line = f"{p['action'].capitalize()} PR [#{pr['number']}]({pr['html_url']}) in [{repo}]({url}): *{pr['title']}*"
    elif t == "IssuesEvent":
        i = p["issue"]; line = f"{p['action'].capitalize()} issue [#{i['number']}]({i['html_url']}) in [{repo}]({url}): *{i['title']}*"
    elif t == "CreateEvent" and p.get("ref_type") == "repository":
        line = f"Created [{repo}]({url})"
    elif t == "ReleaseEvent":
        r = p["release"]; line = f"Released [{r['tag_name']}]({r['html_url']}) in [{repo}]({url})"
    else:
        continue
    if line in seen: continue
    seen.add(line); lines.append(f"- {line} <sub>{age(e['created_at'])}</sub>")
    if len(lines) >= MAX_LINES: break

block = "\n".join(lines) if lines else "- Quiet week."
readme = open("README.md", encoding="utf-8").read()
new = re.sub(f"{re.escape(START)}.*?{re.escape(END)}", f"{START}\n{block}\n{END}", readme, flags=re.S)
if new != readme:
    open("README.md", "w", encoding="utf-8", newline="\n").write(new)
    print("updated"); print(block)
else:
    print("no change")
