"""Export compact provenance from private metadata, never raw source content."""
import csv
import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    playlist = json.loads((ROOT / 'work/playlist.raw.json').read_text(encoding='utf-8-sig'))
    chapters = json.loads((ROOT / 'chapters.json').read_text(encoding='utf8'))
    chapter_for = {lecture: c for c in chapters for lecture in c['lectures']}
    rows = []
    for i, entry in enumerate(playlist['entries'], 1):
        base = ROOT / f"work/sources/{i:02}-{entry['id']}.info"
        metadata = json.loads(Path(str(base) + '.json').read_text(encoding='utf8'))
        caption = Path(str(base) + '.official.vtt')
        normalized = caption.with_suffix('.json')
        cues = json.loads(normalized.read_text(encoding='utf8')) if normalized.exists() else []
        c = chapter_for[i]
        fragment = ROOT / f"chapters/ch{c['number']:02}.html"
        anchors = []
        if fragment.exists():
            soup = BeautifulSoup(fragment.read_text(encoding='utf8'), 'html.parser')
            for a in soup.select('a.timestamp'):
                if f"v={entry['id']}" in a.get('href', ''):
                    section = a.find_parent('section')
                    anchors.append({'chapter': c['number'], 'section': section.get('id') if section else None,
                                    'url': a['href'], 'label': a.get_text(' ', strip=True)})
        rows.append({
            'lecture': i, 'video_id': entry['id'], 'playlist_title': entry['title'],
            'url': f"https://www.youtube.com/watch?v={entry['id']}",
            'duration_seconds': metadata.get('duration'),
            'upload_date': metadata.get('upload_date'),
            'chapter': c['number'],
            'caption_status': 'acquired' if cues else 'missing',
            'caption_provider_label': 'English - NPTEL Official' if cues else None,
            'caption_category': 'subtitles rather than automatic_captions in extractor metadata',
            'caption_sha256': sha(caption) if caption.exists() else None,
            'caption_cues': len(cues),
            'caption_first_seconds': cues[0]['start'] if cues else None,
            'caption_last_seconds': cues[-1]['end'] if cues else None,
            'evidence_file_observed_utc': datetime.fromtimestamp(caption.stat().st_mtime, timezone.utc).isoformat() if caption.exists() else None,
            'coverage': {'identity': 'full', 'textual_acquisition': 'full' if cues else 'blocked',
                         'textual_analysis': 'topic and selected-span review; chapter-specific maps where available',
                         'visual': 'not-performed', 'direct_audio': 'not-performed',
                         'temporal': 'caption-span-addressable' if cues else 'metadata-only'},
            'section_links': anchors,
            'limitation': 'No claim of exhaustive spoken-detail or blackboard reconstruction; formulas are independently developed and reviewed.'
        })
    payload = {'course_title': playlist['title'], 'course_id': '111106097',
               'lecturer': 'T. E. Venkata Balaji', 'institution': 'IIT Madras',
               'playlist_url': 'https://www.youtube.com/playlist?list=PLbMVogVj5nJSNj24jdPGivlJtxbxua2by',
               'official_course_url': 'https://nptel.ac.in/courses/111106097',
               'recordings': rows,
               'publication_boundary': 'Original notes and compact metadata only; captions, source media and signed retrieval URLs are private.'}
    (ROOT / 'source-manifest.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf8')
    with (ROOT / 'lecture-inventory.csv').open('w', encoding='utf8', newline='') as stream:
        fields = ['lecture', 'video_id', 'playlist_title', 'url', 'duration_seconds', 'chapter',
                  'caption_status', 'caption_first_seconds', 'caption_last_seconds']
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: r[field] for field in fields} for r in rows)
    table = []
    for r in rows:
        links = ' · '.join(f'<a href="chapter-{a["chapter"]:02}.html#{a["section"]}">{html.escape(a["label"])}</a>'
                           for a in r['section_links'])
        span = f'{r["caption_first_seconds"]}–{r["caption_last_seconds"]} s' if r['caption_status'] == 'acquired' else 'Unresolved'
        table.append(f'<tr><td>{r["lecture"]}</td><td><a href="{r["url"]}">{html.escape(r["playlist_title"])}</a></td><td>{r["duration_seconds"]} s</td><td>{span}</td><td><a href="chapter-{r["chapter"]:02}.html">Chapter {r["chapter"]}</a><br>{links}</td></tr>')
    body = '''<p class="eyebrow">Source provenance</p><h1>42 recordings and coverage</h1>
<p class="lede">Every recording in the supplied playlist is mapped to a chapter. The edition develops the course's mathematical topics in original prose; it is not a transcript or a claim to reproduce every board calculation.</p>
<p>The <a href="https://nptel.ac.in/courses/111106097">official NPTEL course</a> and the supplied playlist identify the course and lecturer. Playlist upload titles are retained below; their abbreviated wording can omit hypotheses that the chapter statements supply. Chapter numbering follows the fifteen topic modules.</p>
<p class="source-note">Coverage dimensions are separate. Official-label English caption tracks were acquired privately and used for topic mapping and selected source-span checks. The table shows their actual first/last cues, not a claimed percentage of lecture content reproduced. Direct audio listening and blackboard/frame review were not performed. Uncaptioned introductions, silence, or final seconds are not reconstructed. Automatic and official captions can both contain mathematical transcription errors.</p>
<p>Inspect the <a href="source-manifest.json">machine-readable source manifest</a> or <a href="lecture-inventory.csv">CSV inventory</a>. Hashes identify the private caption evidence without redistributing it.</p>
<table><thead><tr><th>Lecture</th><th>Recording</th><th>Duration</th><th>Caption cue span</th><th>Notes and section locators</th></tr></thead><tbody>''' + ''.join(table) + '</tbody></table>'
    output = ROOT / 'frontmatter/source-map.html'
    output.parent.mkdir(exist_ok=True)
    output.write_text(body, encoding='utf8')
    print('Exported', len(rows), 'recordings;', sum(r['caption_status'] == 'acquired' for r in rows), 'caption tracks acquired')


if __name__ == '__main__':
    main()
