import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from benchmark.dataset import FaultSession, SnapshotStore, load_case
from benchmark.evaluation import aggregate, entities_match, evaluate, fact_matches
from benchmark.models import BenchmarkCase, BenchmarkRun, CheckResult

ROOT = Path(__file__).resolve().parents[2] / "benchmarks"


@pytest.fixture
def case():
    return load_case(ROOT / "examples/github_release_001.json")


def run_for(case, **overrides):
    data = dict(
        case_id=case.id,
        case_revision=case.revision,
        snapshot_id=case.environment.snapshot_id,
        agent_version="test",
        model_config_data={"model": "fixture"},
        evaluator_version="1",
        final_answer="v1.4.0, 2026-08-20",
        outcome="answered",
        tool_trace=[],
        run_status="completed",
        latency_ms=10,
        tool_calls=0,
    )
    return BenchmarkRun(**(data | overrides))


def results_for(case):
    return [
        CheckResult(check_id=c.id, score=1, reason="fixture") for c in case.evaluation_rule.checks
    ]


def test_all_categories_and_snapshot_integrity():
    store = SnapshotStore(ROOT / "snapshots/demo-v1/manifest.json")
    cases = [load_case(path) for path in (ROOT / "examples").glob("*.json")]
    assert len({case.category for case in cases}) == 5
    for case in cases:
        store.validate_case(case)
    assert store.search("demo-agent")
    assert store.search("demo-agent release")
    assert store.fetch("https://unknown.invalid") == {}


def test_exported_schema_is_current():
    assert json.loads((ROOT / "schema.json").read_text()) == BenchmarkCase.model_json_schema()


def test_gold_is_not_in_agent_input(case):
    public = case.agent_input()
    assert set(public) == {"task", "allowed_tools", "limits"}
    text = json.dumps(public)
    for forbidden in (
        "ground_truth",
        "evaluation_rule",
        "v1.4.0",
        "e_release",
        "fault_scenario_id",
    ):
        assert forbidden not in text


@pytest.mark.parametrize("mutation", ["reference", "weight", "duplicate", "type", "target"])
def test_invalid_contracts_are_rejected(case, mutation):
    data = case.model_dump(mode="json")
    if mutation == "reference":
        data["ground_truth"]["facts"][0]["evidence_ids"] = ["unknown"]
    elif mutation == "weight":
        data["evaluation_rule"]["dimension_weights"]["process"] = 0.9
    elif mutation == "duplicate":
        data["ground_truth"]["facts"][1]["id"] = "f_version"
    elif mutation == "type":
        data["ground_truth"]["facts"][0]["expected"] = {"type": "boolean", "value": "true"}
    else:
        data["evaluation_rule"]["checks"][0]["target"] = ["e_release"]
    with pytest.raises(ValidationError):
        BenchmarkCase.model_validate(data)


def test_fact_normalization_and_dates(case):
    version, date = case.ground_truth.facts
    version_check, date_check = case.evaluation_rule.checks[:2]
    assert fact_matches(version.expected, "1.4.0", version_check)
    assert not fact_matches(version.expected, "v1.5.0rc1", version_check)
    assert fact_matches(date.expected, "2026-08-20", date_check)
    assert fact_matches(date.expected, "2026-08-21T01:00:00+08:00", date_check)
    assert not fact_matches(date.expected, "2026-08-21", date_check)


def test_alternate_entities_and_wrong_relationship():
    case = load_case(ROOT / "examples/multi_hop_001.json")
    req = case.ground_truth.entity_requirements
    check = case.evaluation_rule.checks[0]
    submitted = [
        {req.dedup_key: e.key, **{key: value.value for key, value in e.facts.items()}}
        for e in req.eligible_entities[1:]
    ]
    assert entities_match(case, submitted, check)
    wrong = copy.deepcopy(submitted)
    wrong[0]["release_date"] = wrong[1]["release_date"]
    assert not entities_match(case, wrong, check)
    assert not entities_match(case, [submitted[0]] * 3, check)


def test_required_failure_cannot_be_offset(case):
    results = results_for(case)
    results[-1].score = 0
    result = aggregate(case, run_for(case), results)
    assert result.total_score == pytest.approx(0.9)
    assert result.passed is False


def test_scoring_repeatable_and_budget_enforced(case):
    results = results_for(case)
    run = run_for(case)
    assert aggregate(case, run, results) == aggregate(case, run, results)
    assert aggregate(case, run, results).passed is True
    assert aggregate(case, run_for(case, latency_ms=121000), results).passed is False
    assert aggregate(case, run_for(case, run_status="agent_error"), results).passed is False
    assert aggregate(case, run_for(case, outcome="insufficient_evidence"), results).passed is False


def test_missing_results_and_judge_failures_are_not_agent_zeroes(case):
    missing = aggregate(case, run_for(case), results_for(case)[:-1])
    assert missing.grading_status == "evaluation_error"
    assert missing.total_score is None and missing.passed is None
    failed = evaluate(case, run_for(case), {})
    assert failed.grading_status == "evaluation_error"
    assert failed.total_score is None


def test_unsupported_citations_and_wrong_version_use_evaluator_results(case):
    # Content entailment is an adapter decision, never inferred from URL existence.
    def adapter(case, run, check):
        return CheckResult(
            check_id=check.id,
            score=0 if check.evaluator == "citation_support" else 1,
            reason="Citation describes the wrong version"
            if check.evaluator == "citation_support"
            else "OK",
        )

    result = evaluate(
        case, run_for(case), {c.evaluator: adapter for c in case.evaluation_rule.checks}
    )
    assert result.grading_status == "completed"
    assert result.passed is False


def test_faults_are_reproducible_and_scoped():
    store = SnapshotStore(ROOT / "snapshots/demo-v1/manifest.json")
    fault = store.manifest.faults[0]
    session = FaultSession(fault)
    assert session.intercept("web_search", {}) is None
    assert session.intercept(fault.tool, fault.arguments)["error"] == "timeout"
    assert session.intercept(fault.tool, fault.arguments) is None
    assert FaultSession(fault).intercept(fault.tool, fault.arguments)["error"] == "timeout"


def test_tampered_and_escaping_artifacts_rejected(tmp_path):
    manifest = json.loads((ROOT / "snapshots/demo-v1/manifest.json").read_text())
    manifest["artifacts"] = manifest["artifacts"][:1]
    artifact = manifest["artifacts"][0]
    (tmp_path / artifact["path"]).write_text("tampered")
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="hash mismatch"):
        SnapshotStore(path)
    artifact["path"] = "../escape.json"
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="escapes"):
        SnapshotStore(path)


def test_live_mode_is_reserved(case):
    case.environment.mode = "live"
    assert evaluate(case, run_for(case), {}).grading_status == "evaluation_error"
