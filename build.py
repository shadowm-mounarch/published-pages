"""Build the static Reading Room locally from an explicit catalog."""
from pathlib import Path
from html import escape
import json
import math
import re
from datetime import date
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'docs'
MD = MarkdownIt('commonmark', {'html': False, 'linkify': False}).enable('table')
BASE = 'https://shadowm-mounarch.github.io/published-pages/'


def shell(title, description, body, document=False):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} · The Reading Room</title><meta name="description" content="{escape(description, quote=True)}">
<meta name="color-scheme" content="light dark"><link rel="icon" href="assets/mark.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/style.css"><script src="assets/site.js" defer></script></head>
<body class="{'document-page' if document else 'index-page'}"><a class="skip" href="#main">Skip to content</a>
<header class="masthead"><a class="brand" href="./"><span class="brand-mark" aria-hidden="true">R<span>↗</span></span><span>The Reading Room<small>MAHMOUD SHARIF ATA</small></span></a>
<div class="header-right"><span class="edition">An independent collection</span><button class="theme" type="button" aria-label="Switch color theme">◐</button></div></header>
{body}<footer class="footer"><span>The Reading Room <span aria-hidden="true">/</span> Mahmoud Sharif Ata</span><a href="#top">Back to top ↑</a></footer>
<div class="toast" role="status" aria-live="polite"></div></body></html>'''


def document(item, source):
    soup = BeautifulSoup(MD.render(source), 'html.parser')
    first = soup.find(['h1', 'h2'])
    if first and first.get_text(' ', strip=True).casefold() == item['title'].casefold():
        first.decompose()
    headings = soup.find_all(re.compile('^h[1-6]$'))
    minimum = min((int(h.name[1]) for h in headings), default=2)
    toc = []
    used = set()
    for h in headings:
        level = min(6, max(2, int(h.name[1]) - minimum + 2))
        h.name = f'h{level}'
        label = h.get_text(' ', strip=True)
        base = re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-') or 'section'
        anchor, count = base, 2
        while anchor in used:
            anchor = f'{base}-{count}'
            count += 1
        used.add(anchor)
        h['id'] = anchor
        if level == 2:
            toc.append(f'<a href="#{anchor}">{escape(label)}</a>')
    for a in soup.find_all('a', href=True):
        if urlsplit(a['href']).scheme in ('http', 'https'):
            a['rel'] = 'noopener noreferrer'
    for table in soup.find_all('table'):
        wrapper = soup.new_tag('div', attrs={'class': 'table-scroll', 'tabindex': '0', 'role': 'region', 'aria-label': 'Scrollable table'})
        table.wrap(wrapper)
    for p in soup.find_all(['p', 'blockquote']):
        text = p.get_text(strip=True)
        letters = re.findall(r'[A-Za-z\u0600-\u06ff]', text)
        if letters and sum('\u0600' <= c <= '\u06ff' for c in letters) / len(letters) > .8:
            p['dir'] = 'rtl'
            p['lang'] = 'ar'
    minutes = max(1, math.ceil(len(re.findall(r'\S+', source)) / 220))
    links = len(soup.select('a[href^="https://"],a[href^="http://"]'))
    stats = f'{minutes} min read <span>·</span> {links} linked references' if links else f'{minutes} min read'
    body = f'''<main id="main"><div id="top"></div><div class="document-intro"><a class="back" href="./">← Collection</a>
<p class="eyebrow">{escape(item['category'])} <span>/</span> REFERENCE NOTE</p><h1>{escape(item['title'])}</h1>
<p class="deck">{escape(item['summary'])}</p><div class="metadata"><time datetime="{item['date']}">{date.fromisoformat(item['date']).strftime('%d %B %Y')}</time><span>·</span>{stats}</div>
<div class="document-tools"><button type="button" data-copy>Copy page link ↗</button><button type="button" data-print>Print / save PDF</button><a href="sources/{item['slug']}.md" download>Download Markdown ↓</a></div></div>
<div class="reading-layout"><aside class="contents"><details open><summary>ON THIS PAGE</summary><nav aria-label="Document contents">{''.join(toc)}</nav></details><div class="side-note">A place to return to.<br>Read, follow the sources,<br>keep the useful parts.</div></aside>
<article class="prose">{soup}</article></div><div class="endnote"><span aria-hidden="true">✳</span> End of document <a href="./">Explore the collection ↗</a></div></main>'''
    return shell(item['title'], item['summary'], body, True)


def build():
    items = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
    slugs = set()
    for item in items:
        for field in ('slug', 'title', 'category', 'summary', 'date'):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f'Missing or empty {field}')
        slug = item['slug']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in slugs:
            raise ValueError(f'Invalid or duplicate slug: {slug}')
        slugs.add(slug)
        date.fromisoformat(item['date'])
        source = (ROOT / 'content' / f'{slug}.md').read_text(encoding='utf-8')
        if not source.strip():
            raise ValueError(f'Empty document: {slug}')
        item['_source'] = source
    OUT.mkdir(exist_ok=True)
    (OUT / 'sources').mkdir(exist_ok=True)
    (OUT / 'assets').mkdir(exist_ok=True)
    for asset in (ROOT / 'assets').iterdir():
        if asset.is_file():
            (OUT / 'assets' / asset.name).write_bytes(asset.read_bytes())
    cards = []
    for n, item in enumerate(items, 1):
        source = item['_source']
        (OUT / f'{item["slug"]}.html').write_text(document(item, source), encoding='utf-8')
        (OUT / 'sources' / f'{item["slug"]}.md').write_text(source, encoding='utf-8')
        search = escape(f'{item["title"]} {item["category"]} {item["summary"]}'.lower(), quote=True)
        cards.append(f'''<a class="document-card" href="{item['slug']}.html" data-search="{search}"><div class="card-top"><span>{escape(item['category'])}</span><span class="card-number">{n:02}</span></div><h3>{escape(item['title'])}</h3><p>{escape(item['summary'])}</p><div class="card-bottom"><time datetime="{item['date']}">{date.fromisoformat(item['date']).strftime('%d %b %Y')}</time><span>Read document <span aria-hidden="true">↗</span></span></div></a>''')
    body = f'''<main id="main"><section class="hero" id="top"><div><p class="eyebrow"><span class="status-dot"></span> RESEARCH &amp; WORKING NOTES</p><h1>Good ideas deserve<br>a place to <em>live.</em></h1><p class="hero-description">A growing collection of research, references, and considered plans.<br class="desktop-break"> Made to be read. Kept within reach.</p><a class="hero-link" href="#collection">Explore the collection <span>↓</span></a></div><div class="hero-art" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="orbit orbit-three"></div><div class="art-center">R<span>↗</span></div><span class="art-note">NOTES BECOME<br>POSSIBILITIES.</span><span class="art-index">EST. 2026 / VOL. 01</span></div></section>
<section id="collection" class="collection"><div class="collection-heading"><div><p class="eyebrow">THE COLLECTION</p><h2>Open a new thread.</h2></div><span class="count">{len(items):02} DOCUMENT{'S' if len(items) != 1 else ''}</span></div><div class="search-row"><label for="search">Find something worth reading</label><div class="search-box"><span aria-hidden="true">⌕</span><input id="search" type="search" placeholder="Search by title or topic…" autocomplete="off"></div></div><p class="search-status sr-only" role="status" aria-live="polite"></p><div class="cards">{''.join(cards)}</div><p class="empty" hidden>No documents match. Try another title or topic.</p></section><section class="colophon"><span class="colophon-symbol" aria-hidden="true">✳</span><p>Knowledge, kept close.</p><span>Research with sources.<br>Plans with a purpose.</span></section></main>'''
    (OUT / 'index.html').write_text(shell('Collection', 'Research and reference notes by Mahmoud Sharif Ata.', body), encoding='utf-8')
    (OUT / '404.html').write_text(shell('Page not found', 'Return to the Reading Room.', '<main id="main" class="document-intro"><div id="top"></div><h1>This page has moved<br>out of reach.</h1><p class="deck">Find your next read in the collection.</p><a href="/published-pages/">Return to the collection ↗</a></main>'), encoding='utf-8')
    (OUT / '.nojekyll').touch()
    print(f'Built {len(items)} documents and collection locally.')


if __name__ == '__main__':
    build()
