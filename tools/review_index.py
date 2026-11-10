"""Collect actual independent review records into a public audit index."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    records = []
    for path in sorted((ROOT / 'validation/reviews').glob('ch*.json')):
        record = json.loads(path.read_text(encoding='utf8'))
        record['record'] = path.relative_to(ROOT).as_posix()
        records.append(record)
    result = {'reviews': records, 'scope': 'Actual agent editorial reports; no claim of human or formal-proof certification.'}
    (ROOT / 'validation/review-index.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf8')
    print('Indexed', len(records), 'review records')


if __name__ == '__main__':
    main()
