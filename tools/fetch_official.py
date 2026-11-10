"""Fetch NPTEL's human caption tracks from already acquired video metadata."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import requests
from acquire import parse_vtt

ROOT = Path(__file__).resolve().parents[1]


def fetch(path):
    data = json.loads(path.read_text(encoding='utf8'))
    if not data.get('duration'):
        return
    output = path.with_suffix('.official.vtt')
    tracks = data.get('subtitles', {})
    items = [(lang, item) for lang, values in tracks.items()
             if lang.startswith('en') for item in values if item['ext'] == 'vtt']
    if not items:
        return path.name, 'NO OFFICIAL ENGLISH TRACK'
    if not output.exists():
        response = requests.get(items[0][1]['url'], timeout=45)
        response.raise_for_status()
        output.write_text(response.text, encoding='utf8')
    rows = parse_vtt(output)
    output.with_suffix('.json').write_text(json.dumps(rows, ensure_ascii=False), encoding='utf8')
    # Five-minute paragraphs preserve lecture order without caption-line noise.
    buckets = {}
    for row in rows:
        bucket = int(row['start'] // 300)
        buckets.setdefault(bucket, []).append(row['text'])
    text = '\n\n'.join(f'[{b * 5:02d}:00] ' + ' '.join(parts)
                        for b, parts in buckets.items())
    output.with_suffix('.txt').write_text(text, encoding='utf8')
    return path.name, len(rows), round(rows[-1]['end']), data['duration']


if __name__ == '__main__':
    paths = sorted((ROOT / 'work/sources').glob('*.info.json'))
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(fetch, paths):
            if result:
                print(*result)
