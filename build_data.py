"""Build data/posts.js from the Substack export: published posts and phase.

Pass --covers to also fetch each post's cover image from Substack (slow, rate-limited).
"""
import csv, json, os, re, sys, time, urllib.error, urllib.request

BASE = "https://alyssafuward.substack.com/p/"
PHASES = [  # (start date inclusive, id, name)
    ("2022-01-01", "career", "Career notes"),
    ("2023-06-01", "quiet", "The quiet stretch"),
    ("2024-12-01", "return", "The return"),
    ("2025-11-01", "framework", "The framework"),
    ("2026-02-11", "build", "Building with AI"),
    ("2026-08-11", "step", "A new step"),
]

def phase(d):
    return [p for p in PHASES if p[0] <= d][-1][1]

def cover(url):
    for wait in (5, 15, 45, 90):
        try:
            html = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20).read().decode("utf8", "ignore")
            break
        except urllib.error.HTTPError as e:
            if e.code != 429:
                return None
            time.sleep(wait)
    else:
        return None
    m = re.search(r'property="og:image" content="([^"]+)"', html)
    if not m:
        return None
    return m.group(1).replace("w_1200,h_675", "w_480,h_270")

rows = [r for r in csv.DictReader(open("data/posts.csv")) if r["is_published"] == "true"]
rows.sort(key=lambda r: r["post_date"])
posts = []
for i, r in enumerate(rows, 1):
    slug = r["post_id"].split(".", 1)[1]
    d = r["post_date"][:10]
    posts.append({"n": i, "date": d, "title": r["title"], "subtitle": r["subtitle"],
                  "url": BASE + slug, "phase": phase(d), "type": r["type"], "paid": r["audience"] != "everyone"})
# Substack rate-limits, so fetch slowly and cache what we get
CACHE = "data/covers.json"
covers = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
for p in posts:
    if "--covers" not in sys.argv:
        p["cover"] = None
        continue
    if not covers.get(p["url"]):
        covers[p["url"]] = cover(p["url"])
        json.dump(covers, open(CACHE, "w"), indent=1)
        time.sleep(1.5)
    p["cover"] = covers[p["url"]]
open("data/posts.js", "w").write("window.POSTS = " + json.dumps(posts, ensure_ascii=False, indent=1) + ";\n"
    + "window.PHASES = " + json.dumps([{"id": i, "name": n, "start": s} for s, i, n in PHASES]) + ";\n")
print(len(posts), "posts;", sum(1 for p in posts if p["cover"]), "with covers")
