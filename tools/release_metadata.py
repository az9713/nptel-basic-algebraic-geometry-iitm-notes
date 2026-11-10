"""Build compact public release metadata from the actual authored artifacts."""
import hashlib
import json
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def canonical_hash(path):
    return hashlib.sha256(path.read_text(encoding='utf8').encode('utf8')).hexdigest()


def main():
    inventory = json.loads((ROOT / 'chapters.json').read_text(encoding='utf8'))
    sources = json.loads((ROOT / 'source-manifest.json').read_text(encoding='utf8'))
    reviews = json.loads((ROOT / 'validation/review-index.json').read_text(encoding='utf8'))
    chapters = []
    for chapter in inventory:
        n = chapter['number']
        path = ROOT / f'chapters/ch{n:02}.html'
        soup = BeautifulSoup(path.read_text(encoding='utf8'), 'html.parser')
        chapter['sections'] = [
            {'id': section.get('id'), 'heading': section.h2.get_text(' ', strip=True),
             'recording_locators': [a['href'] for a in section.select('a.timestamp')],
             'evidence_class': 'independently authored exposition/proofs/examples; lecture topic spine',
             'external_inputs': [a['href'] for a in section.select('a[href]')
                                 if a['href'].startswith('https://') and 'youtube.com' not in a['href']]}
            for section in soup.select('section') if section.h2]
        chapter['manuscript_sha256_lf'] = canonical_hash(path)
        chapter['exercise_count'] = len(soup.select('section#exercises > ol > li'))
        chapter['word_count_including_tex'] = len(soup.get_text(' ').split())
        chapters.append(chapter)
    ir = {'chapters': chapters, 'source_manifest': 'source-manifest.json',
          'evidence_limits': 'Caption-topic and span analysis varies by chapter; no full direct audio or blackboard/frame review.',
          'reuse_policy': 'No content-reuse percentage asserted; exposition is original synthesis, not a transcript.'}
    (ROOT / 'analysis-ir.json').write_text(json.dumps(ir, indent=2, ensure_ascii=False) + '\n', encoding='utf8', newline='\n')
    completion = {
        'manuscript_status': 'complete study edition accepted for release',
        'chapters': len(chapters), 'recordings': len(sources['recordings']),
        'worked_exercises': sum(c['exercise_count'] for c in chapters),
        'words_including_tex': sum(c['word_count_including_tex'] for c in chapters),
        'independent_reviews': len(reviews['reviews']),
        'review_evidence': 'validation/review-index.json',
        'source_evidence': 'source-manifest.json',
        'checks': {name: json.loads((ROOT / 'validation' / name).read_text(encoding='utf8'))['status']
                   for name in ['algebra-results.json', 'geometry-results.json', 'browser-results.json', 'package-results.json']},
        'publication_boundary': 'This records pre-publication acceptance. Remote state is verified separately in GitHub workflow and Pages deployment records.',
        'limitations': ['AI-agent editorial review, not human refereeing or formal proof certification',
                        'No exhaustive audiovisual reconstruction',
                        'Invoked general theorems remain cited inputs',
                        'Dated Jacobian research reports not independently reproduced']
    }
    (ROOT / 'completion.json').write_text(json.dumps(completion, indent=2) + '\n', encoding='utf8', newline='\n')
    artifacts = []
    for path in sorted(ROOT.glob('*.html')):
        artifacts.append({'path': path.name, 'sha256_lf': canonical_hash(path),
                          'purpose': 'portable reader page', 'canonical_input': 'chapters/' if path.name.startswith('chapter-') else 'frontmatter/'})
    artifacts += [{'path': name, 'sha256_lf': canonical_hash(ROOT / name),
                   'purpose': purpose} for name, purpose in [
                       ('algebra_lab.py', 'exact finite algebra checks'),
                       ('source-manifest.json', 'compact recording evidence'),
                       ('analysis-ir.json', 'chapter/source/claim-role structure')]]
    (ROOT / 'artifact-manifest.json').write_text(json.dumps({'artifacts': artifacts}, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps(completion))


if __name__ == '__main__':
    main()
