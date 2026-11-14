"""Verify generated documents, citations, and browser behavior locally."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from urllib.parse import unquote, urlsplit
import contextlib
import json
import re

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from build import ROOT, OUT, MD


def verify():
    records = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
    evidence = ROOT / 'verification'
    evidence.mkdir(exist_ok=True)
    results = []
    for entry in records:
        slug = entry['slug']
        source = (ROOT / 'content' / f'{slug}.md').read_text(encoding='utf-8')
        assert (OUT / 'sources' / f'{slug}.md').read_text(encoding='utf-8') == source
        original = BeautifulSoup(MD.render(source), 'html.parser')
        generated = BeautifulSoup((OUT / f'{slug}.html').read_text(encoding='utf-8'), 'html.parser')
        expected_links = [a['href'] for a in original.select('a[href]')]
        actual_links = [a['href'] for a in generated.select('.prose a[href]')]
        assert expected_links == actual_links, f'Citation mismatch: {slug}'
        first = original.find(['h1', 'h2'])
        if first and first.get_text(' ', strip=True).casefold() == entry['title'].casefold():
            first.decompose()
        normalize = lambda s: re.sub(r'\s+', ' ', s).strip()
        assert normalize(original.get_text(' ', strip=True)) == normalize(generated.select_one('.prose').get_text(' ', strip=True)), f'Content mismatch: {slug}'
        assert len(generated.select('h1')) == 1
        results.append(f'{slug}: full content, source download, and {len(actual_links)} citations preserved')
    for path in OUT.glob('*.html'):
        soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
        for node in soup.select('[href], [src]'):
            target = node.get('href', node.get('src'))
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            relative = unquote(parsed.path)
            if relative.startswith('/published-pages/'):
                relative = relative[len('/published-pages/'):]
            elif relative.startswith('/'):
                raise AssertionError(f'Unexpected absolute local URL: {target}')
            dest = path.parent / relative if relative else path
            if dest.is_dir():
                dest = dest / 'index.html'
            assert dest.exists(), f'Broken link {path.name}: {target}'
            if parsed.fragment:
                dest_soup = soup if dest == path else BeautifulSoup(dest.read_text(encoding='utf-8'), 'html.parser')
                assert dest_soup.find(id=unquote(parsed.fragment)), f'Broken anchor: {target}'
    results.append('All local links, downloads, assets, and table-of-contents anchors resolve')
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(OUT)))
    Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/'
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel='msedge', headless=True)
            context = browser.new_context(viewport={'width': 1440, 'height': 1100}, color_scheme='light')
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(url)
            page.screenshot(path=str(evidence / 'collection-desktop.png'), full_page=True)
            if records:
                page.locator('#search').fill('no-document-matches-this-query')
                assert page.locator('.document-card:visible').count() == 0
                assert page.locator('.empty').is_visible()
                page.locator('#search').fill(records[0]['title'])
                assert page.locator('.document-card:visible').count() == 1
                page.locator('#search').fill('')
            page.get_by_role('button', name='Switch to dark theme').click()
            assert page.locator('html').get_attribute('data-theme') == 'dark'
            page.reload()
            assert page.locator('html').get_attribute('data-theme') == 'dark'
            page.screenshot(path=str(evidence / 'collection-dark.png'), full_page=True)
            page.get_by_role('button', name='Switch to light theme').click()
            for record in records:
                page.goto(url + record['slug'] + '.html')
                assert page.locator('h1').inner_text() == record['title']
                assert page.locator('html').evaluate('(el) => el.scrollWidth <= innerWidth')
                page.screenshot(path=str(evidence / f'{record["slug"]}-desktop.png'), full_page=True)
                page.emulate_media(media='print')
                assert page.locator('.document-tools').is_hidden()
                page.emulate_media(media='screen')
            page.set_viewport_size({'width': 390, 'height': 844})
            for target in [''] + [r['slug'] + '.html' for r in records]:
                page.goto(url + target)
                assert page.locator('html').evaluate('(el) => el.scrollWidth <= innerWidth'), f'Mobile overflow: {target}'
                page.screenshot(path=str(evidence / f'{target.removesuffix(".html") or "collection"}-mobile.png'), full_page=True)
            assert not errors, f'Browser errors: {errors}'
            browser.close()
        results.append('Desktop/mobile browser checks passed: search, empty state, theme persistence, print styles, overflow, and JavaScript errors')
    finally:
        server.shutdown()
        server.server_close()
    (evidence / 'checks.txt').write_text('\n'.join(results) + '\n', encoding='utf-8')
    print('\n'.join(results))


if __name__ == '__main__':
    verify()
