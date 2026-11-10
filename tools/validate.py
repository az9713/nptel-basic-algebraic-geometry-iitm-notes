"""Validate the published reader and fail on incomplete course/review state."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_math(text, label, issues):
    tokens = re.findall(r'\\[()\[\]]', text)
    stack = []
    for token in tokens:
        if token in (r'\(', r'\['):
            if stack:
                issues.append(f'{label}: nested math delimiters')
            stack.append(token)
        elif not stack or stack.pop() != {r'\)': r'\(', r'\]': r'\['}[token]:
            issues.append(f'{label}: mismatched math delimiter')
    if stack:
        issues.append(f'{label}: unclosed math delimiter')
    for expression in re.findall(r'\\\((.*?)\\\)|\\\[(.*?)\\\]', text, re.S):
        math = ''.join(expression)
        # HTML entities are safe; literal comparisons in math are not.
        if '<' in math or '>' in math:
            issues.append(f'{label}: literal comparison sign inside math')
        depth = 0
        for char in re.sub(r'\\[{}]', '', math):
            depth += (char == '{') - (char == '}')
            if depth < 0:
                issues.append(f'{label}: unmatched TeX brace')
                break
        if depth:
            issues.append(f'{label}: unmatched TeX braces')
    if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', text):
        issues.append(f'{label}: control character in manuscript')
    if re.search(r'\\\\[)\]]', text):
        issues.append(f'{label}: extra backslash before closing math delimiter')


def validate(release=True):
    issues = []
    diagnostics = []
    chapters = json.loads((ROOT / 'chapters.json').read_text(encoding='utf8'))
    if sorted(n for chapter in chapters for n in chapter['lectures']) != list(range(1, 43)):
        issues.append('Chapter inventory does not cover exactly lectures 1..42')
    for chapter in chapters:
        n = chapter['number']
        fragment = ROOT / f'chapters/ch{n:02}.html'
        page = ROOT / f'chapter-{n:02}.html'
        if not fragment.exists() or not page.exists():
            issues.append(f'Chapter {n}: manuscript or built page missing')
            continue
        text = fragment.read_text(encoding='utf8')
        soup = BeautifulSoup(text, 'html.parser')
        words = len(soup.get_text(' ').split())
        diagnostics.append({'chapter': n, 'words_including_tex': words,
                            'sections': len(soup.select('section')),
                            'math_spans': text.count(r'\(') + text.count(r'\['),
                            'sha256': digest(fragment)})
        if not soup.select('details') or not soup.select('ol > li'):
            issues.append(f'Chapter {n}: exercises/worked solutions missing')
        if not soup.select('a.timestamp'):
            issues.append(f'Chapter {n}: recording locators missing')
        if re.search(r'\[(?:PROOF|CITATION|TODO|NUMBER).*?\]|lorem ipsum', text, re.I):
            issues.append(f'Chapter {n}: unresolved placeholder')
        inspect_math(text, fragment.name, issues)
        if release:
            accepted = []
            expected_author = ('root' if n <= 7 else 'affine_projective' if n <= 10
                               else 'local_functions' if n <= 13 else 'geometric_local')
            for record_path in (ROOT / 'validation/reviews').glob(f'ch{n:02}-*.json'):
                record = json.loads(record_path.read_text(encoding='utf8'))
                if record.get('chapter') != n:
                    issues.append(f'Chapter {n}: mismatched chapter in review record')
                if record.get('reviewer') not in {'root', 'affine_projective', 'local_functions', 'geometric_local'}:
                    issues.append(f'Chapter {n}: missing or unknown reviewer identity')
                if 'full' not in str(record.get('review_kind', '')).lower():
                    issues.append(f'Chapter {n}: full-review scope not recorded')
                if record.get('author') != expected_author:
                    issues.append(f'Chapter {n}: inconsistent recorded author')
                if not (ROOT / record.get('report', 'missing-report')).is_file():
                    issues.append(f'Chapter {n}: review report missing')
                if (record.get('status') == 'accepted' and record.get('final_sha256') == digest(fragment)
                        and record.get('author') == expected_author
                        and record.get('reviewer') in {'root', 'affine_projective', 'local_functions', 'geometric_local'}
                        and record.get('chapter') == n
                        and 'full' in str(record.get('review_kind', '')).lower()):
                    accepted.append(record)
            reviewers = {record.get('reviewer') for record in accepted
                         if record.get('reviewer') != record.get('author')}
            if len(reviewers) < 2:
                issues.append(f'Chapter {n}: fewer than two independent accepted reviews at current hash')
    pages = sorted(ROOT.glob('*.html'))
    soups = {path.name: BeautifulSoup(path.read_text(encoding='utf8'), 'html.parser') for path in pages}
    for name, soup in soups.items():
        if not soup.title or not soup.html or soup.html.get('lang') != 'en':
            issues.append(f'{name}: missing title or language')
        if not soup.find('meta', attrs={'name': 'viewport'}):
            issues.append(f'{name}: missing viewport')
        ids = [element['id'] for element in soup.select('[id]')]
        if len(ids) != len(set(ids)):
            issues.append(f'{name}: duplicate ids')
        for element in soup.select('[href], [src]'):
            raw = element.get('href', element.get('src', ''))
            parsed = urlsplit(raw)
            if parsed.scheme or parsed.netloc or not raw:
                continue
            target = unquote(parsed.path) or name
            path = ROOT / target
            if not path.exists():
                issues.append(f'{name}: missing local target {raw}')
                continue
            if parsed.fragment and target in soups:
                if not soups[target].find(id=unquote(parsed.fragment)):
                    issues.append(f'{name}: missing anchor {raw}')
    manifest_path = ROOT / 'source-manifest.json'
    if release and not manifest_path.exists():
        issues.append('Public source manifest missing')
    if manifest_path.exists():
        records = json.loads(manifest_path.read_text(encoding='utf8'))['recordings']
        if len(records) != 42 or len({r['video_id'] for r in records}) != 42:
            issues.append('Source manifest must contain 42 distinct requested recordings')
        for r in records:
            if r.get('caption_status') != 'acquired':
                issues.append(f"Lecture {r['lecture']}: caption evidence unresolved")
            for link in r.get('section_links', []):
                match = re.search(r'[?&]t=(\d+)s', link['url'])
                if match and int(match.group(1)) > r['duration_seconds']:
                    issues.append(f"Lecture {r['lecture']}: locator beyond recording duration")
    if release:
        for required in ['index.html', 'study-guide.html', 'source-map.html',
                         'laboratory.html', 'references.html', 'about.html',
                         'validation/algebra-results.json', 'validation/geometry-results.json',
                         'validation/browser-results.json']:
            if not (ROOT / required).exists():
                issues.append(f'Missing release artifact: {required}')
        for required in ['algebra-results.json', 'geometry-results.json', 'browser-results.json']:
            path = ROOT / 'validation' / required
            if path.exists():
                report = json.loads(path.read_text(encoding='utf8'))
                if report.get('status') != 'passed':
                    issues.append(f'Required check did not pass: {required}')
                if required == 'browser-results.json':
                    assets = {path.relative_to(ROOT).as_posix(): hashlib.sha256(
                        path.read_text(encoding='utf8').encode('utf8')).hexdigest()
                        for path in sorted((ROOT / 'assets').rglob('*')) if path.is_file()}
                    if report.get('assets_sha256_lf') != assets:
                        issues.append('Browser evidence missing or stale for reader assets')
                    by_page = {row['page']: row for row in report.get('pages', [])}
                    for page in pages:
                        row = by_page.get(page.name, {})
                        current = hashlib.sha256(page.read_text(encoding='utf8').encode('utf8')).hexdigest()
                        if row.get('content_sha256_lf') != current:
                            issues.append(f'{page.name}: browser evidence missing or stale')
                        if row.get('math_errors') or row.get('javascript_errors') or row.get('overflow_desktop') or row.get('overflow_mobile'):
                            issues.append(f'{page.name}: failed browser check')
    return {'status': 'passed' if not issues else 'failed', 'release_mode': release,
            'issues': sorted(set(issues)), 'chapters': diagnostics,
            'scope': 'mechanical completeness, links, math syntax and review hashes; not a mathematical proof checker'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--draft', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = validate(not args.draft)
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    print(payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + '\n', encoding='utf8')
    raise SystemExit(0 if result['status'] == 'passed' else 1)


if __name__ == '__main__':
    main()
