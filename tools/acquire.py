"""Normalize private VTT evidence; never publish the raw text."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / 'work' / 'sources'


def seconds(value):
    h, m, s = value.split(':')
    return float(h) * 3600 + float(m) * 60 + float(s)


def parse_vtt(path):
    blocks = re.split(r'\n\s*\n', path.read_text(encoding='utf-8-sig'))
    rows = []
    previous = ''
    for block in blocks:
        lines = block.splitlines()
        mark = next((i for i, line in enumerate(lines) if ' --> ' in line), None)
        if mark is None:
            continue
        start, end = lines[mark].split(' --> ')
        text = html.unescape(re.sub(r'<[^>]+>', '', ' '.join(lines[mark + 1:])))
        text = re.sub(r'\s+', ' ', text).strip()
        if text and text != previous:
            # YouTube rolling captions repeat a prefix; human tracks do not.
            clean = text[len(previous):].strip() if text.startswith(previous) else text
            if clean:
                rows.append({'start': seconds(start), 'end': seconds(end.split()[0]),
                             'text': clean})
        previous = text
    return rows


def main():
    for path in sorted(PRIVATE.glob('*.en.vtt')):
        rows = parse_vtt(path)
        path.with_suffix('.json').write_text(json.dumps(rows, ensure_ascii=False), encoding='utf8')
        chunks = []
        for row in rows:
            stamp = int(row['start'])
            chunks.append(f"[{stamp // 60:02d}:{stamp % 60:02d}] {row['text']}")
        path.with_suffix('.txt').write_text('\n'.join(chunks), encoding='utf8')
        print(path.name, len(rows), round(rows[-1]['end'], 2) if rows else 0)


if __name__ == '__main__':
    main()
