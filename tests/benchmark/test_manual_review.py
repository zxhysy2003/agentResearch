import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from langchain_core.language_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage

from benchmark.review import summarize
from benchmark.runner import ROOT, run_dataset


class FinalOnlyModel(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


@pytest_asyncio.fixture
async def experiment(tmp_path):
    """Synthetic answer and reviews exercise bookkeeping, not agent correctness."""
    output = tmp_path / "experiment"
    await run_dataset(
        output=output,
        case_ids=["github_lookup_04"],
        model_factory=lambda: FinalOnlyModel(
            responses=[AIMessage(content='{"answer":"Synthetic fixture","outcome":"answered"}')]
        ),
        model_config={"model": "synthetic-fixture"},
    )
    return output


def fill_review(output: Path) -> dict:
    path = output / "run-0001/review.json"
    review = json.loads(path.read_text())
    review["reviewer"] = "synthetic test reviewer"
    for check in review["checks"]:
        check.update(score=1, reason="Synthetic test score, not a capability result")
    path.write_text(json.dumps(review))
    return review


@pytest.mark.asyncio
async def test_ungraded_then_graded_then_reopened_does_not_keep_stale_score(experiment):
    initial = summarize(experiment)
    assert initial["mean_score_among_graded"] is None
    review = fill_review(experiment)
    summary = summarize(experiment)
    assert summary["graded_runs"] == 1
    assert summary["grading_coverage"] == 1
    assert summary["pass_rate_among_graded"] == 1
    review["checks"][0]["score"] = None
    (experiment / "run-0001/review.json").write_text(json.dumps(review))
    summary = summarize(experiment)
    assert summary["graded_runs"] == 0 and summary["ungraded_runs"] == 1
    assert summary["mean_score_among_graded"] is None
    assert json.loads((experiment / "run-0001/evaluation.json").read_text()) == {
        "grading_status": "ungraded"
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "problem", ["missing", "duplicate", "identity", "score", "reason", "reviewer", "reference"]
)
async def test_invalid_reviews_are_not_valid_scores(experiment, problem):
    review = fill_review(experiment)
    if problem == "missing":
        review["checks"].pop()
    elif problem == "duplicate":
        review["checks"].append(review["checks"][0])
    elif problem == "identity":
        review["case_id"] = "different-case"
    elif problem == "score":
        review["checks"][0]["score"] = 2
    elif problem == "reason":
        review["checks"][0]["reason"] = ""
    elif problem == "reviewer":
        review["reviewer"] = ""
    else:
        review["checks"][0]["evidence_refs"] = ["unknown-evidence"]
    (experiment / "run-0001/review.json").write_text(json.dumps(review))
    summary = summarize(experiment)
    assert summary["invalid_reviews"] == 1
    assert summary["graded_runs"] == 0
    assert summary["runs"][0]["total_score"] is None
    assert summary["runs"][0]["error"]


@pytest.mark.asyncio
@pytest.mark.parametrize("filename", ["run.json", "case.json"])
async def test_changed_artifacts_cannot_reuse_old_review(experiment, filename):
    fill_review(experiment)
    path = experiment / "run-0001" / filename
    path.write_text(path.read_text() + "\n")
    summary = summarize(experiment)
    assert summary["invalid_reviews"] == 1
    assert "changed" in summary["runs"][0]["error"]


@pytest.mark.asyncio
async def test_missing_run_sidecar_does_not_leave_a_valid_score(experiment):
    fill_review(experiment)
    (experiment / "run-0001/error.json").unlink()
    summary = summarize(experiment)
    assert summary["invalid_reviews"] == 1
    assert summary["runs"][0]["total_score"] is None
    assert summary["runs"][0]["passed"] is None


@pytest.mark.asyncio
async def test_required_zero_cannot_be_offset_by_other_scores(experiment):
    review = fill_review(experiment)
    review["checks"][-1]["score"] = 0
    (experiment / "run-0001/review.json").write_text(json.dumps(review))
    summary = summarize(experiment)
    assert summary["graded_runs"] == 1
    assert summary["runs"][0]["total_score"] > 0
    assert summary["runs"][0]["passed"] is False


@pytest.mark.asyncio
async def test_grade_validate_schema_do_not_import_service_credentials(experiment, tmp_path):
    env = {
        key: value for key, value in os.environ.items() if "KEY" not in key and "TOKEN" not in key
    }
    env["PYTHONPATH"] = str(ROOT / "src")
    script = (
        "import runpy,sys; sys.modules['core']=None; "
        "sys.argv=['benchmark',*sys.argv[1:]]; runpy.run_module('benchmark',run_name='__main__')"
    )
    commands = [
        ["grade", "--run-dir", str(experiment)],
        ["schema", str(tmp_path / "schema.json")],
        [
            "validate",
            str(ROOT / "benchmarks/datasets/github_lookup_v1/cases/github_lookup_01.json"),
        ],
    ]
    for args in commands:
        result = subprocess.run(
            [sys.executable, "-c", script, *args], env=env, capture_output=True, text=True, cwd=ROOT
        )
        assert result.returncode == 0, result.stderr


@pytest.mark.asyncio
async def test_grade_cli_returns_nonzero_for_invalid_review(experiment):
    review = fill_review(experiment)
    review["checks"].pop()
    (experiment / "run-0001/review.json").write_text(json.dumps(review))
    env = os.environ | {"PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "benchmark", "grade", "--run-dir", str(experiment)],
        env=env,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "invalid=1" in result.stdout
