"""Deterministic matching and aggregation; semantic decisions stay auditable."""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from benchmark.models import (
    BenchmarkCase,
    BenchmarkRun,
    Check,
    CheckResult,
    EvaluationResult,
    Expected,
)


def fact_matches(expected: Expected, actual: Any, check: Check) -> bool:
    """Compare an extracted value. Extraction must cite the final answer, not gold data."""
    value = expected.value
    if expected.type == "number":
        return type(actual) in (int, float) and abs(actual - value) <= check.tolerance
    if expected.type == "boolean":
        return type(actual) is bool and actual == value
    if expected.type == "set":
        if not isinstance(actual, list) or not all(isinstance(x, str) for x in actual):
            return False
        return (
            set(value) <= set(actual)
            if check.set_match == "contains"
            else set(value) == set(actual)
        )
    if not isinstance(actual, str):
        return False
    if expected.type == "datetime":
        try:
            left = datetime.fromisoformat(value.replace("Z", "+00:00"))
            right = datetime.fromisoformat(actual.replace("Z", "+00:00"))
            if right.tzinfo is None:
                # A bare date is unambiguous only for a day-granularity check in UTC.
                if check.precision != "day" or len(actual) != 10:
                    return False
                right = right.replace(tzinfo=UTC)
            left, right = left.astimezone(UTC), right.astimezone(UTC)
            return left.date() == right.date() if check.precision == "day" else left == right
        except ValueError:
            return False
    if check.normalizer == "version_tag":
        return actual.removeprefix("v") == value.removeprefix("v")
    return actual == value


def entities_match(case: BenchmarkCase, submitted: list[dict[str, Any]], check: Check) -> bool:
    requirements = case.ground_truth.entity_requirements
    if requirements is None or len(submitted) != requirements.count:
        return False
    eligible = {entity.key: entity for entity in requirements.eligible_entities}
    seen: set[str] = set()
    for item in submitted:
        key = item.get(requirements.dedup_key)
        if not isinstance(key, str) or key in seen or key not in eligible:
            return False
        seen.add(key)
        if not all(
            field in item and fact_matches(eligible[key].facts[field], item[field], check)
            for field in requirements.required_fields
        ):
            return False
    return True


def aggregate(
    case: BenchmarkCase, run: BenchmarkRun, results: list[CheckResult]
) -> EvaluationResult:
    """Missing/duplicate results and identity mismatches are grading errors, never zeroes."""

    def error(message: str) -> EvaluationResult:
        return EvaluationResult(
            case_id=case.id,
            check_results=results,
            grading_status="evaluation_error",
            error=message,
        )

    if (run.case_id, run.case_revision, run.snapshot_id) != (
        case.id,
        case.revision,
        case.environment.snapshot_id,
    ):
        return error("Run does not match case revision and snapshot")
    checks = case.evaluation_rule.checks
    by_id = {result.check_id: result for result in results}
    if len(by_id) != len(results) or set(by_id) != {check.id for check in checks}:
        return error("Every check must have exactly one result")
    scores = {}
    for dimension, weight in case.evaluation_rule.dimension_weights.items():
        if weight == 0:
            continue
        selected = [check for check in checks if check.dimension == dimension]
        scores[dimension] = sum(by_id[c.id].score * c.weight for c in selected) / sum(
            c.weight for c in selected
        )
    total = sum(scores[d] * w for d, w in case.evaluation_rule.dimension_weights.items() if w)
    within_budget = (
        run.tool_calls == len(run.tool_trace)
        and run.tool_calls <= case.environment.limits.max_tool_calls
        and run.latency_ms <= case.environment.limits.timeout_seconds * 1000
    )
    if run.tool_calls != len(run.tool_trace):
        return error("Tool call count does not match trace")
    passed = (
        total >= case.evaluation_rule.pass_threshold
        and all(by_id[c.id].score == 1 for c in checks if c.required)
        and run.run_status == "completed"
        and run.outcome == case.ground_truth.expected_outcome
        and within_budget
    )
    return EvaluationResult(
        case_id=case.id,
        check_results=results,
        dimension_scores=scores,
        total_score=total,
        passed=passed,
        grading_status="completed",
    )


Evaluator = Callable[[BenchmarkCase, BenchmarkRun, Check], CheckResult]


def evaluate(
    case: BenchmarkCase, run: BenchmarkRun, evaluators: dict[str, Evaluator]
) -> EvaluationResult:
    """Adapters own extraction/judging. A missing or failed adapter fails grading explicitly."""
    results = []
    try:
        if case.environment.mode != "snapshot":
            raise ValueError("Live evaluation is reserved but not supported in v1")
        for check in case.evaluation_rule.checks:
            result = evaluators[check.evaluator](case, run, check)
            if result.check_id != check.id:
                raise ValueError("Evaluator returned the wrong check ID")
            results.append(result)
    except Exception as exc:
        return EvaluationResult(
            case_id=case.id,
            check_results=results,
            grading_status="evaluation_error",
            error=f"{type(exc).__name__}: {exc}",
        )
    return aggregate(case, run, results)
