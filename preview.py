#!/usr/bin/env python3
"""Transform dist/ into a clickable preview under preview/.

Two differences from the real site, both required by the artifact host:
  - the CSS is inlined into every page, so a preview can never render unstyled
  - index.html drops its own doctype/html/head/body, because the host wraps the
    main page in a skeleton; every other page keeps its own, since they are
    served as plain files.
Nothing else changes: same copy, same markup, same generated product pages.
"""
import io, os, re, shutil, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST, PREV = os.path.join(ROOT,"dist"), os.path.join(ROOT,"preview")
css = "\n".join(io.open(os.path.join(DIST,c),encoding="utf-8").read() for c in ("tokens.css","site.css"))

if os.path.isdir(PREV): shutil.rmtree(PREV)
os.makedirs(os.path.join(PREV,"crops"))

def inline(html, depth):
    html = re.sub(r'<link rel="stylesheet" href="[^"]*tokens\.css">\s*<link rel="stylesheet" href="[^"]*site\.css">',
                  "<style>\n"+css.replace('url("fonts/', 'url("'+("../"*depth)+'fonts/')+"\n</style>", html)
    return html

n = 0
for src in glob.glob(os.path.join(DIST,"*.html")) + glob.glob(os.path.join(DIST,"crops","*.html")):
    rel = os.path.relpath(src, DIST)
    depth = 1 if rel.startswith("crops") else 0
    html = inline(io.open(src,encoding="utf-8").read(), depth)
    if rel == "index.html":
        # the host supplies the skeleton for the main page only
        html = re.sub(r"^<!doctype html>\s*<html[^>]*>\s*<head>\s*<meta charset=\"utf-8\">\s*"
                      r"<meta name=\"viewport\"[^>]*>\s*", "", html, flags=re.I)
        html = html.replace("</head><body>", '<meta name="claude:viewport-fit-sides" content="cover">\n')
        html = re.sub(r"</body></html>\s*$", "", html)
    io.open(os.path.join(PREV,rel),"w",encoding="utf-8").write(html)
    n += 1
shutil.copytree(os.path.join(DIST,"fonts"), os.path.join(PREV,"fonts"))
print(f"preview: {n} pages, css inlined, fonts copied")
print("index.html starts:", io.open(os.path.join(PREV,"index.html"),encoding="utf-8").read()[:60].replace("\n","⏎"))
