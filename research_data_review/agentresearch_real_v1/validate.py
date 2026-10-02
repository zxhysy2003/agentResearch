"""Offline provenance validation. Does not claim to verify semantic entailment."""
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / 'src'))
from benchmark.dataset import SnapshotStore, load_case
from collect import Text


def main():
    store = SnapshotStore(ROOT / 'manifest.json')
    assert store.manifest.synthetic is False
    paths = sorted((ROOT / 'cases').glob('*/*.json'))
    cases = [load_case(p) for p in paths]
    expected = {name: 10 for name in ('github_lookup', 'official_docs', 'comparison', 'multi_hop', 'edge_case')}
    counts = Counter(c.category for c in cases)
    assert dict(counts) == expected
    assert len({c.id for c in cases}) == 50
    jsonl = [json.loads(line) for line in (ROOT / 'dataset.jsonl').read_text().splitlines()]
    assert {c['id']: c for c in jsonl} == {c.id: c.model_dump(mode='json') for c in cases}
    cited = set()
    for case in cases:
        store.validate_case(case)
        source_ids = {e.artifact_id for e in case.ground_truth.evidence}
        cited.update(source_ids)
        if case.category in ('comparison', 'multi_hop'):
            assert len(source_ids) >= 2, case.id
        assert all(e.captured_at <= case.task.as_of for e in case.ground_truth.evidence)
        assert case.environment.fault_scenario_id is None
        public = case.agent_input()
        assert set(public) == {'task', 'allowed_tools', 'limits'}
    assert cited == {a.id for a in store.manifest.artifacts}
    downloaded = []
    for file in sorted((ROOT / 'sources').glob('*/metadata.json')):
        m = json.loads(file.read_text())
        raw = (file.parent / 'body').read_bytes()
        assert hashlib.sha256(raw).hexdigest() == m['sha256']
        assert len(raw) == m['bytes']
        text = raw.decode('utf-8', errors='replace')
        if '<html' in text[:2000].lower() or '<!doctype html' in text[:100].lower():
            parser = Text(); parser.feed(text); text = '\n'.join(parser.parts)
        assert text == (file.parent / 'text.txt').read_text()
        downloaded.append(m)
    annotations = json.loads((ROOT / 'annotation_checks.json').read_text())
    assert {a['case_id'] for a in annotations} == {c.id for c in cases}
    fact_count = 0
    anchor_count = 0
    for annotation in annotations:
        case = next(c for c in cases if c.id == annotation['case_id'])
        extracted = []
        for check in annotation['checks']:
            path = ROOT / 'sources' / check['source']
            if check['kind'] == 'json_pointer':
                value = json.loads((path / 'body').read_text())
                for part in check['pointer'].strip('/').split('/') if check['pointer'] else []:
                    value = value[int(part)] if isinstance(value, list) else value[part]
                assert value == check['value']
                extracted.append(value)
                fact_count += 1
            else:
                text = (path / 'text.txt').read_text()
                start = text.find(check['anchor'])
                assert start >= 0
                assert text[:start].count('\n') + 1 == check['line']
                anchor_count += 1
        assert extracted == [f.expected.value for f in case.ground_truth.facts]
    # Independently verify observed exceptions used by boundary annotations.
    def body(key): return json.loads((ROOT / 'sources' / key / 'body').read_text())
    assert body('releases_pgvector') == [] and body('pgvector_tags')
    assert body('releases_awesome_python') == []
    assert body('repo_requests_async')['archived'] is True
    assert body('repo_autogpt_plugins')['archived'] is True
    assert body('repo_old_fastapi')['full_name'] == 'fastapi/fastapi'
    assert body('repo_old_langchain')['full_name'] == 'langchain-ai/langchain'
    assert body('releases_celery')[0]['prerelease'] is True
    assert body('latest_celery')['prerelease'] is False
    assert body('repo_pgvector')['license']['spdx_id'] == 'NOASSERTION'
    assert 'shutdown' not in (ROOT / 'sources/python_queue/text.txt').read_text().lower()
    summary = dict(
        validated_at=datetime.now(timezone.utc).isoformat(),
        cases=len(cases), category_counts=dict(counts),
        cited_sources=len(cited), downloaded_sources=len(downloaded),
        machine_checked_fact_values=fact_count, matched_source_anchors=anchor_count,
        schema_validation='passed', source_hashes='passed',
        factual_extraction_consistency='passed', derived_text_consistency='passed',
        synthetic=False, semantic_annotation_review='pending_human_review',
        limitations=['Text anchors prove location, not semantic entailment.',
                     'These are benchmark candidates; no Agent run or grading result is fabricated.'],
    )
    (ROOT / 'validation_report.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
