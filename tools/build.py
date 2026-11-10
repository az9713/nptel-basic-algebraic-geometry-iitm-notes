"""Assemble public pages from authored HTML fragments and public metadata."""
import html
import json
import sys
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def page(title, body, chapters, current=None):
    entries = ''.join(f'<li><a {"aria-current=page" if c["number"] == current else ""} href="chapter-{c["number"]:02}.html">{html.escape(c["title"])}</a></li>' for c in chapters)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Independent lecture notes for NPTEL Basic Algebraic Geometry, IIT Madras.">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; object-src 'none'; base-uri 'none'">
<title>{html.escape(title)} — Basic Algebraic Geometry</title><link rel="stylesheet" href="assets/book.css">
<script defer src="assets/math-config.js"></script><script defer src="assets/mathjax-tex-svg.js"></script><script defer src="assets/book.js"></script><script defer src="assets/curves.js"></script></head>
<body><a class="skip" href="#main">Skip to content</a><header><a href="index.html">BASIC ALGEBRAIC GEOMETRY</a><div class="toolbar-controls"><button data-action="theme" type="button">Theme</button> <button data-action="print" type="button">Print / PDF</button></div></header>
<div class="layout"><aside><nav aria-label="Course contents"><details open><summary>Chapters and resources</summary><ol>{entries}</ol><p><a href="study-guide.html">Study guide</a><br><a href="source-map.html">42 recordings and coverage</a><br><a href="laboratory.html">Algebra laboratory</a><br><a href="figures.html">Explore curves and tangents</a><br><a href="references.html">Sources and attribution</a><br><a href="about.html">Verification and limitations</a></p></details></nav></aside>
<main id="main">{body}<footer>Independent study edition · NPTEL / IIT Madras lecture spine · Original exposition and exercises. No institutional endorsement.</footer></main></div></body></html>'''


def main():
    chapters = json.loads((ROOT / 'chapters.json').read_text())
    for c in chapters:
        n = c['number']
        if '--partial' in sys.argv and not (ROOT / f'chapters/ch{n:02}.html').exists():
            continue
        body = (ROOT / f'chapters/ch{n:02}.html').read_text(encoding='utf8')
        soup = BeautifulSoup(body, 'html.parser')
        toc = '<nav class="toc" aria-label="Chapter sections"><ul>' + ''.join(f'<li><a href="#{h.parent.get("id", h.get("id", ""))}">{h.get_text(" ")}</a></li>' for h in soup.select('section > h2')) + '</ul></nav>'
        heading = f'<p class="eyebrow">Chapter {n} · Lectures {c["lectures"][0]}–{c["lectures"][-1]}</p><h1>{html.escape(c["title"])}</h1>{toc}'
        prev = f'<a href="chapter-{n-1:02}.html">Previous chapter</a>' if n > 1 else '<a href="index.html">Course home</a>'
        nxt = f'<a href="chapter-{n+1:02}.html">Next chapter</a>' if n < len(chapters) else '<a href="study-guide.html">Study guide</a>'
        output = page(c['title'], heading + body + f'<nav class="pager" aria-label="Chapter navigation">{prev}{nxt}</nav>', chapters, n)
        (ROOT / f'chapter-{n:02}.html').write_text(output, encoding='utf8')
    for fragment in sorted((ROOT / 'frontmatter').glob('*.html')):
        body = fragment.read_text(encoding='utf8')
        if '<!-- CHAPTER_LIST -->' in body:
            tags = {
                1: 'equations ideal radical nullstellensatz topology',
                2: 'irreducibility prime connected',
                3: 'noetherian components decomposition',
                4: 'dimension krull height hypersurface transcendence',
                5: 'spectrum maxspec coordinate ring functor',
                6: 'basic open localization denominator',
                7: 'regular functions quasi compact sheaf',
                8: 'morphism duality automorphism jacobian punctured plane',
                9: 'projective charts gluing separated diagonal',
                10: 'homogeneous graded projective localization homogenization',
                11: 'germ local ring maximal ideal',
                12: 'rational function field',
                13: 'veronese projective global constant embedding',
                14: 'birational local isomorphism stalk',
                15: 'tangent cotangent smooth nonsingular jacobian'
            }
            items = []
            for c in chapters:
                query = html.escape((c['title'] + ' ' + tags[c['number']]).lower(), quote=True)
                items.append(f'<li data-search="{query}"><a href="chapter-{c["number"]:02}.html">{c["title"]}</a><br><span class="meta">Lectures {c["lectures"][0]}–{c["lectures"][-1]}</span></li>')
            body = body.replace('<!-- CHAPTER_LIST -->', '<ol class="chapter-list">' + ''.join(items) + '</ol>')
        soup = BeautifulSoup(body, 'html.parser')
        title = soup.h1.get_text() if soup.h1 else fragment.stem
        (ROOT / fragment.name).write_text(page(title, body, chapters), encoding='utf8')
    print(f'Built {len(chapters)} chapters and front matter')


if __name__ == '__main__':
    main()
