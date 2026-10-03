"""Human review input and reports; unreviewed runs never become fabricated zeroes."""

import json
from pathlib import Path
from statistics import mean
from typing import Any, Literal

from pydantic import Field

from benchmark.evaluation import aggregate
from benchmark.models import (
    BenchmarkCase,
    BenchmarkRun,
    CheckResult,
    Contract,
    EvaluationResult,
    Score,
)
from benchmark.runner import EVALUATOR_VERSION, digest, write_json


class ReviewCheck(Contract):
    check_id: str
    score: Score | None = None
    reason: str = ""
    evidence_refs: list[str] = Field(default_factory=list)


class ManualReview(Contract):
    run_id: str
    case_id: str
    case_revision: int
    snapshot_id: str
    run_sha256: str
    case_sha256: str
    evaluator_version: Literal["manual-v1"] = "manual-v1"
    reviewer: str = ""
    checks: list[ReviewCheck]


def make_review(
    case: BenchmarkCase,
    run: BenchmarkRun,
    run_id: str,
    run_sha256: str,
    case_sha256: str,
) -> ManualReview:
    return ManualReview(
        run_id=run_id,
        case_id=run.case_id,
        case_revision=run.case_revision,
        snapshot_id=run.snapshot_id,
        run_sha256=run_sha256,
        case_sha256=case_sha256,
        checks=[ReviewCheck(check_id=check.id) for check in case.evaluation_rule.checks],
    )


def evaluate_review(directory: Path, run_id: str) -> tuple[BenchmarkRun, EvaluationResult | None]:
    run_bytes = (directory / "run.json").read_bytes()
    case_bytes = (directory / "case.json").read_bytes()
    run = BenchmarkRun.model_validate_json(run_bytes)
    case = BenchmarkCase.model_validate_json(case_bytes)
    review = ManualReview.model_validate_json((directory / "review.json").read_bytes())
    identity = (run_id, run.case_id, run.case_revision, run.snapshot_id)
    if identity != (review.run_id, review.case_id, review.case_revision, review.snapshot_id):
        raise ValueError("review identity does not match run")
    if (case.id, case.revision, case.environment.snapshot_id) != identity[1:]:
        raise ValueError("case identity does not match run")
    if review.run_sha256 != digest(run_bytes) or review.case_sha256 != digest(case_bytes):
        raise ValueError("run or case changed after the review template was generated")
    if run.evaluator_version != EVALUATOR_VERSION:
        raise ValueError("unsupported evaluator version")
    ids = [check.check_id for check in review.checks]
    if len(ids) != len(set(ids)) or set(ids) != {check.id for check in case.evaluation_rule.checks}:
        raise ValueError("review must contain every check exactly once")
    allowed_refs = {evidence.id for evidence in case.ground_truth.evidence}
    for check in review.checks:
        if not set(check.evidence_refs) <= allowed_refs:
            raise ValueError("unknown evidence reference in review")
        if check.score is not None and not check.reason.strip():
            raise ValueError("each scored check needs a reason")
    if any(check.score is None for check in review.checks):
        return run, None
    if not review.reviewer.strip():
        raise ValueError("completed review needs a reviewer name")
    results = [
        CheckResult(
            check_id=check.check_id,
            score=check.score,
            reason=check.reason,
            evidence_refs=check.evidence_refs,
        )
        for check in review.checks
        if check.score is not None
    ]
    return run, aggregate(case, run, results)


def summarize(output: Path) -> dict:
    """Validate current review files on each invocation; do not trust stale evaluations."""
    experiment = json.loads((output / "experiment.json").read_text("utf-8"))
    rows: list[dict[str, Any]] = []
    seen = set()
    for entry in experiment["runs"]:
        run_id = entry["run_id"]
        if (
            not isinstance(run_id, str)
            or not run_id.startswith("run-")
            or not (run_id.removeprefix("run-").isdigit())
        ):
            raise ValueError("invalid run folder name")
        if run_id in seen:
            raise ValueError("duplicate run ID in experiment")
        seen.add(run_id)
        directory = output / run_id
        if not directory.resolve().is_relative_to(output.resolve()):
            raise ValueError("run folder escapes experiment")
        row: dict[str, Any] = {
            **entry,
            "run_status": "unknown",
            "grading_status": "ungraded",
            "total_score": None,
            "passed": None,
            "latency_ms": None,
            "tool_calls": None,
            "token_usage": {},
            "error": None,
        }
        try:
            run = BenchmarkRun.model_validate_json((directory / "run.json").read_bytes())
            row.update(
                run_status=run.run_status,
                latency_ms=run.latency_ms,
                tool_calls=run.tool_calls,
                token_usage=run.token_usage,
            )
            if run.case_id != entry["case_id"]:
                raise ValueError("experiment case ID does not match run")
            if run.snapshot_id != experiment["snapshot_id"]:
                raise ValueError("experiment snapshot ID does not match run")
            _, evaluation = evaluate_review(directory, run_id)
            if evaluation is None:
                # Replace a previously graded result when the review becomes incomplete.
                write_json(directory / "evaluation.json", {"grading_status": "ungraded"})
            else:
                write_json(directory / "evaluation.json", evaluation.model_dump(mode="json"))
                row.update(
                    grading_status=evaluation.grading_status,
                    total_score=evaluation.total_score,
                    passed=evaluation.passed,
                    error=evaluation.error,
                )
            if row["error"] is None:
                row["error"] = json.loads((directory / "error.json").read_text("utf-8"))["error"]
        except (OSError, ValueError, KeyError, TypeError) as exc:
            row.update(
                grading_status="evaluation_error",
                total_score=None,
                passed=None,
                error=f"{type(exc).__name__}: {exc}",
            )
            if directory.is_dir():
                write_json(
                    directory / "evaluation.json",
                    {"grading_status": "evaluation_error", "error": row["error"]},
                )
        rows.append(row)
    graded = [row for row in rows if row["grading_status"] == "completed"]
    known_usage = [row for row in rows if row["token_usage"]]
    summary = {
        "snapshot_id": experiment["snapshot_id"],
        "agent_version": experiment["agent_version"],
        "model_config": experiment["model_config"],
        "evaluator_version": experiment["evaluator_version"],
        "total_runs": len(rows),
        "graded_runs": len(graded),
        "ungraded_runs": sum(row["grading_status"] == "ungraded" for row in rows),
        "invalid_reviews": sum(row["grading_status"] == "evaluation_error" for row in rows),
        "run_failures": sum(
            row["run_status"] in ("agent_error", "budget_exceeded") for row in rows
        ),
        "grading_coverage": len(graded) / len(rows) if rows else 0,
        "pass_rate_among_graded": mean(row["passed"] for row in graded) if graded else None,
        "mean_score_among_graded": mean(row["total_score"] for row in graded) if graded else None,
        "mean_latency_ms": mean(row["latency_ms"] for row in rows if row["latency_ms"] is not None)
        if any(row["latency_ms"] is not None for row in rows)
        else None,
        "mean_tool_calls": mean(row["tool_calls"] for row in rows if row["tool_calls"] is not None)
        if any(row["tool_calls"] is not None for row in rows)
        else None,
        "runs_with_known_token_usage": len(known_usage),
        "total_tokens": sum(row["token_usage"].get("total_tokens", 0) for row in known_usage)
        if rows and len(known_usage) == len(rows)
        else None,
        "runs": rows,
    }
    write_json(output / "summary.json", summary)
    lines = [
        "# AgentResearch benchmark report",
        "",
        f"Snapshot: `{summary['snapshot_id']}`. Agent: `{summary['agent_version']}`.",
        "",
        f"Runs: {len(rows)}. Graded: {len(graded)}. "
        f"Ungraded: {summary['ungraded_runs']}. Invalid reviews: {summary['invalid_reviews']}.",
        f"Run failures: {summary['run_failures']}. "
        f"Grading coverage: {summary['grading_coverage']:.1%}.",
        "",
        "Pass rate and mean score include only valid, completed reviews; "
        "ungraded results are not zeroes. This is a development-set baseline.",
        "",
        f"Pass rate among graded: {summary['pass_rate_among_graded']}. "
        f"Mean score among graded: {summary['mean_score_among_graded']}.",
        f"Mean latency (ms): {summary['mean_latency_ms']}. "
        f"Mean tool calls: {summary['mean_tool_calls']}.",
        f"Token usage known for {len(known_usage)}/{len(rows)} runs. "
        f"Total tokens: {summary['total_tokens'] if summary['total_tokens'] is not None else 'unknown'}.",
        "",
        "| Run | Case | Attempt | Run status | Grading | Score | Passed |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        case_label = str(row["case_id"]).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| [{row['run_id']}]({row['run_id']}/run.json) | {case_label} | {row['attempt']} | "
            f"{row['run_status']} | {row['grading_status']} | {row['total_score']} | {row['passed']} |"
        )
    lines.extend(["", "Errors:", ""])
    for row in rows:
        if row["error"]:
            lines.append(f"- {row['run_id']}: {row['error']}")
    if not any(row["error"] for row in rows):
        lines.append("None.")
    (output / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary
