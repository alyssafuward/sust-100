"""Rebuild versions/: a playable, frozen copy of the game at each checkpoint, plus an index page.

Add a checkpoint by appending to CHECKPOINTS (slug, commit, title, note), then run:
    python3 tools/make_versions.py
Each copy is built from git, so it looks and plays exactly like it did at that commit.
"""
import html, os, shutil, subprocess

CHECKPOINTS = [
    ("01-first-mockup", "065499d", "First mockup", "Auto-runs forward, pop-up cards over the game, clothesline level, workbench wall"),
    ("02-no-autoscroll", "eee7ca1", "No auto-scroll", "The orange only moves while you hold the arrows"),
    ("03-parade-terrain", "5abe9e4", "Parade terrain", "Marchers and signs in different sizes; steps, floats, crates and drums to climb"),
    ("04-new-levels", "addce6a", "New levels + finale", "Parade oranges follow you, truck with a pile, top-down workshop maze, fireworks finale"),
    ("05-jump-only", "651c271", "Jump-only + article bar", "Every step up is a jump; article info moves to a bar under the game"),
    ("06-collect-on-touch", "e0b0c1c", "Collect on touch", "Boxes collect from any side, not just from below"),
    ("07-hometown-street", "ebbd0c2", "Hometown street", "The busy last level: houses, townsfolk, parade oranges with signs, #100 is home"),
    ("08-race-flags", "5eca176", "The race, with flags", "Bandanna, flags and hurdles, small faded town, #100 finish line"),
    ("09-race-boxes", "687e7b6", "The race, with boxes", "Boxes are back, bolder hurdles, 97 posts"),
    ("10-level-menu", "f4705b2", "Level menu", "Levels button to jump to any level from anywhere; links like #parade and #race"),
]
ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "versions")
REPO = "https://github.com/alyssafuward/sust-100"

def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], check=True, capture_output=True, text=True).stdout

def label(n, title):
    # small removable tag so screenshots show which version this is
    return f"""<div id="vlabel" style="position:fixed;top:12px;left:50%;transform:translateX(-50%);z-index:99;display:flex;align-items:center;gap:10px;background:#1F6FA8;color:#fff;font:600 12px 'DM Sans',sans-serif;padding:6px 8px 6px 14px;border-radius:999px;white-space:nowrap">
  v{n} · {html.escape(title)} <a href="../" style="color:#fff">all versions</a>
  <button onclick="this.parentNode.remove()" aria-label="Hide label" style="background:none;border:0;color:#fff;font-size:16px;line-height:1;cursor:pointer">×</button>
</div>
"""

shutil.rmtree(OUT, ignore_errors=True)
cards = []
for i, (slug, commit, title, note) in enumerate(CHECKPOINTS, 1):
    d = os.path.join(OUT, slug)
    os.makedirs(os.path.join(d, "data"))
    page = git("show", f"{commit}:index.html").replace('href="versions/"', 'href="../"')
    page = page.replace("</body>", label(i, title) + "</body>")
    open(os.path.join(d, "index.html"), "w").write(page)
    open(os.path.join(d, "data", "posts.js"), "w").write(git("show", f"{commit}:data/posts.js"))
    date = git("show", "-s", "--format=%ad", "--date=format:%b %-d, %Y", commit).strip()
    cards.append(f"""  <a class="card" href="{slug}/">
    <div class="num">v{i}</div>
    <div class="body"><div class="eyebrow">{date}</div><h2>{html.escape(title)}</h2><p>{html.escape(note)}</p></div>
    <div class="go">Play →</div>
  </a>""")

open(os.path.join(OUT, "index.html"), "w").write(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>100 Posts: Versions</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=DM+Serif+Display&display=swap" rel="stylesheet">
<style>
  :root {{ --pale: #F2F8FD; --mid: #C8DEF0; --deep: #1F6FA8; --ink: #1A1A1A; --grey: #666; --rule: #D8ECF8; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--pale); color: var(--ink); font-family: "DM Sans", system-ui, sans-serif; }}
  main {{ max-width: 760px; margin: 0 auto; padding: 48px 16px 64px; }}
  .eyebrow {{ font-size: 11px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--deep); }}
  h1 {{ font-family: "DM Serif Display", serif; font-weight: 400; font-size: 44px; margin: 8px 0; }}
  .lede {{ color: var(--grey); line-height: 1.5; margin: 0 0 28px; }}
  .lede a {{ color: var(--deep); }}
  .card {{ display: flex; align-items: center; gap: 16px; background: #fff; border-radius: 16px; padding: 18px 20px; margin-bottom: 12px; color: inherit; text-decoration: none; box-shadow: 0 1px 0 var(--rule); }}
  .card:hover {{ box-shadow: 0 6px 20px rgba(31,111,168,.14); }}
  .num {{ font-family: "DM Serif Display", serif; font-size: 28px; color: var(--deep); width: 48px; flex: none; }}
  .body {{ flex: 1; min-width: 0; }}
  .card h2 {{ font-family: "DM Serif Display", serif; font-weight: 400; font-size: 22px; margin: 4px 0; }}
  .card p {{ margin: 0; color: var(--grey); font-size: 14px; line-height: 1.45; }}
  .go {{ color: var(--deep); font-weight: 600; white-space: nowrap; }}
  @media (max-width: 520px) {{ .go {{ display: none; }} .num {{ width: 36px; font-size: 22px; }} }}
</style>
</head>
<body>
<main>
  <div class="eyebrow">100 Posts · behind the scenes</div>
  <h1>Versions</h1>
  <p class="lede">Every checkpoint of the game, frozen and playable, from the first mockup to now. <a href="../">Play the current game</a> · <a href="{REPO}/commits/main">see the history on GitHub</a></p>
{chr(10).join(cards)}
</main>
</body>
</html>
""")
print(f"built {len(CHECKPOINTS)} versions in versions/")
