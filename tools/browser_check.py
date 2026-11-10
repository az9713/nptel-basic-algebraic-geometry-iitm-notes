"""Check every rendered public page at desktop and narrow widths."""
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url')
    parser.add_argument('--chromium', action='store_true', help='Use installed Playwright Chromium instead of system Chrome')
    parser.add_argument('--output', type=Path, default=ROOT / 'validation/browser-results.json')
    args = parser.parse_args()
    records = []
    failures = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**({} if args.chromium else {'channel': 'chrome'}))
        page = browser.new_page(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
        for path in sorted(ROOT.glob('*.html')):
            errors = []
            handler = lambda error: errors.append(str(error))
            page.on('pageerror', handler)
            url = args.base_url.rstrip('/') + '/' + path.name if args.base_url else path.resolve().as_uri()
            response = page.goto(url, wait_until='load')
            # CDP response-body retrieval is unreliable for file: URLs. For a
            # deployed HTTP(S) reader, verify the actual server response.
            loaded = response.text() if args.base_url and response else path.read_text(encoding='utf8')
            loaded_hash = hashlib.sha256(loaded.replace('\r\n', '\n').replace('\r', '\n').encode('utf8')).hexdigest()
            expected_hash = hashlib.sha256(path.read_text(encoding='utf8').encode('utf8')).hexdigest()
            page.wait_for_function('window.MathJax && MathJax.startup && MathJax.startup.document', timeout=45000)
            page.evaluate('MathJax.startup.promise')
            math_errors = page.locator('mjx-merror, [data-mjx-error]').count()
            overflow_desktop = page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
            page.set_viewport_size({'width': 390, 'height': 844})
            overflow_mobile = page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
            record = {'page': path.name, 'math_spans': page.locator('mjx-container').count(),
                      'content_sha256_lf': loaded_hash, 'matches_authored_page': loaded_hash == expected_hash,
                      'math_errors': math_errors, 'javascript_errors': errors,
                      'overflow_desktop': overflow_desktop, 'overflow_mobile': overflow_mobile}
            records.append(record)
            if math_errors or errors or overflow_desktop or overflow_mobile or loaded_hash != expected_hash:
                failures.append(path.name)
            if path.name in ['chapter-01.html', 'chapter-10.html', 'chapter-15.html', 'index.html', 'figures.html']:
                page.screenshot(path=str(ROOT / 'work' / (path.stem + '-mobile.png')), full_page=False)
                page.set_viewport_size({'width': 1440, 'height': 1000})
                page.screenshot(path=str(ROOT / 'work' / (path.stem + '-desktop.png')), full_page=False)
            page.set_viewport_size({'width': 1440, 'height': 1000})
            page.remove_listener('pageerror', handler)
        root_url = args.base_url.rstrip('/') + '/' if args.base_url else ROOT.resolve().as_uri() + '/'
        page.goto(root_url + 'index.html')
        page.locator('#search').fill('birational')
        assert page.locator('.chapter-list li:visible').count() == 1
        page.locator('#search').fill('')
        page.locator('[data-action=theme]').click()
        assert page.locator('html.light').count() == 1
        page.locator('[data-action=theme]').click()
        page.goto(root_url + 'figures.html')
        assert 'Singular' in page.locator('#curve-output').inner_text()
        for endpoint in ['-1.5', '1.5']:
            page.locator('#curve-parameter').fill(endpoint)
            page.locator('#curve-parameter').dispatch_event('input')
            point = page.locator('#curve-chart circle')
            cx, cy, radius = [float(point.get_attribute(attr)) for attr in ['cx', 'cy', 'r']]
            assert radius <= cx <= 680 - radius and radius <= cy <= 420 - radius
        page.select_option('#curve-mode', 'node')
        page.locator('#curve-parameter').fill('1')
        page.locator('#curve-parameter').dispatch_event('input')
        assert 'Singular' in page.locator('#curve-output').inner_text()
        page.locator('#curve-parameter').fill('0')
        page.locator('#curve-parameter').dispatch_event('input')
        assert 'Nonsingular' in page.locator('#curve-output').inner_text()
        page.emulate_media(media='print')
        assert page.locator('aside').evaluate('(e)=>getComputedStyle(e).display') == 'none'
        browser.close()
    result = {'status': 'passed' if not failures else 'failed', 'pages': records,
              'assets_sha256_lf': {
                  path.relative_to(ROOT).as_posix(): hashlib.sha256(
                      path.read_text(encoding='utf8').encode('utf8')).hexdigest()
                  for path in sorted((ROOT / 'assets').rglob('*')) if path.is_file()},
              'failed_pages': failures,
              'interaction_checks': ['chapter search', 'theme toggle', 'cusp singular point',
                                     'cusp slider endpoints remain in view', 'node two-branch point',
                                     'node vertical nonsingular tangent', 'print layout'],
              'source': 'live GitHub Pages' if args.base_url else 'local files',
              'limitations': 'No exhaustive assistive-technology audit or browser print-PDF pagination audit.'}
    args.output.parent.mkdir(exist_ok=True, parents=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'status': result['status'], 'pages': len(records), 'failed': failures}))
    raise SystemExit(bool(failures))


if __name__ == '__main__':
    main()
