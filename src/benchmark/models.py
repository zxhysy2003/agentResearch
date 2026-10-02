"""Versioned benchmark contracts, intentionally separate from the chat API."""

from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

Dimension = Literal["correctness", "evidence", "process"]
Score = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
Outcome = Literal["answered", "partial", "needs_clarification", "insufficient_evidence"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Task(Contract):
    prompt: str = Field(min_length=1)
    as_of: AwareDatetime
    context: dict[str, str] = Field(default_factory=dict)
    requirements: list[str] = Field(default_factory=list)


class Limits(Contract):
    max_tool_calls: int = Field(default=15, gt=0)
    timeout_seconds: float = Field(default=120, gt=0)


class Environment(Contract):
    mode: Literal["snapshot", "live"] = "snapshot"
    snapshot_id: str
    allowed_tools: list[str] = Field(min_length=1)
    limits: Limits = Field(default_factory=Limits)
    fault_scenario_id: str | None = None


class Expected(Contract):
    type: Literal["string", "number", "boolean", "datetime", "set"]
    value: Any

    @model_validator(mode="after")
    def validate_value(self):
        valid = {
            "string": lambda v: isinstance(v, str),
            "number": lambda v: type(v) in (int, float) and float("-inf") < v < float("inf"),
            "boolean": lambda v: type(v) is bool,
            "datetime": lambda v: (
                isinstance(v, str)
                and datetime.fromisoformat(v.replace("Z", "+00:00")).tzinfo is not None
            ),
            "set": lambda v: isinstance(v, list) and all(isinstance(x, str) for x in v),
        }
        try:
            ok = valid[self.type](self.value)
        except ValueError:
            ok = False
        if not ok:
            raise ValueError(f"value does not match expected type {self.type}")
        return self


class Fact(Contract):
    id: str
    subject: str
    predicate: str
    expected: Expected
    evidence_ids: list[str] = Field(min_length=1)


class Evidence(Contract):
    id: str
    source_type: Literal["github_release", "github_api", "official_docs", "repository", "blog"]
    url: str
    artifact_id: str
    locator: str
    captured_at: AwareDatetime


class Rubric(Contract):
    id: str
    criterion: str
    evidence_ids: list[str] = Field(default_factory=list)
    anchors: dict[Literal["0", "0.5", "1"], str]

    @model_validator(mode="after")
    def all_anchors(self):
        if set(self.anchors) != {"0", "0.5", "1"}:
            raise ValueError("rubrics require 0, 0.5 and 1 anchors")
        return self


class Entity(Contract):
    key: str
    facts: dict[str, Expected]
    evidence_ids: list[str] = Field(min_length=1)


class EntityRequirements(Contract):
    count: int = Field(gt=0)
    dedup_key: str
    required_fields: list[str] = Field(min_length=1)
    eligible_entities: list[Entity] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_entities(self):
        keys = [e.key for e in self.eligible_entities]
        if len(set(keys)) != len(keys) or len(keys) < self.count:
            raise ValueError("eligible entities must be unique and satisfy requested count")
        for entity in self.eligible_entities:
            if not set(self.required_fields) <= entity.facts.keys():
                raise ValueError("eligible entity is missing required facts")
        return self


class GroundTruth(Contract):
    expected_outcome: Outcome
    facts: list[Fact] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    rubrics: list[Rubric] = Field(default_factory=list)
    entity_requirements: EntityRequirements | None = None


class Check(Contract):
    id: str
    dimension: Dimension
    evaluator: Literal[
        "fact_match", "rubric_judge", "entity_constraint", "citation_support", "trace_assertion"
    ]
    target: list[str] = Field(min_length=1)
    weight: float = Field(default=1, gt=0, allow_inf_nan=False)
    required: bool = False
    normalizer: Literal["identity", "version_tag"] = "identity"
    precision: Literal["instant", "day"] = "instant"
    tolerance: float = Field(default=0, ge=0, allow_inf_nan=False)
    set_match: Literal["exact", "contains"] = "exact"
    accepted_source_types: list[str] = Field(default_factory=list)
    assertion: (
        Literal["supporting_source_observed", "outcome_matches", "fault_recovered"] | None
    ) = None


class EvaluationRule(Contract):
    checks: list[Check] = Field(min_length=1)
    dimension_weights: dict[Dimension, Score]
    pass_threshold: Score = 0.8

    @model_validator(mode="after")
    def weights_are_valid(self):
        if abs(sum(self.dimension_weights.values()) - 1) > 1e-9:
            raise ValueError("dimension weights must sum to one")
        used = {c.dimension for c in self.checks}
        positive = {d for d, w in self.dimension_weights.items() if w > 0}
        if used != positive:
            raise ValueError("every weighted dimension needs checks; checks need positive weights")
        return self


class BenchmarkCase(Contract):
    schema_version: Literal["1.0"] = "1.0"
    id: str
    revision: int = Field(default=1, gt=0)
    category: Literal["github_lookup", "official_docs", "comparison", "multi_hop", "edge_case"]
    difficulty: Literal["easy", "medium", "hard"]
    tags: list[str] = Field(default_factory=list)
    split: Literal["dev", "test"] = "dev"
    task: Task
    environment: Environment
    ground_truth: GroundTruth
    evaluation_rule: EvaluationRule

    @model_validator(mode="after")
    def references_are_valid(self):
        gt = self.ground_truth
        groups = [gt.facts, gt.evidence, gt.rubrics, self.evaluation_rule.checks]
        ids = [item.id for group in groups for item in group]
        if len(ids) != len(set(ids)) or {"outcome", "entities"} & set(ids):
            raise ValueError("IDs must be unique and must not use reserved target names")
        evidence_ids = {e.id for e in gt.evidence}
        entities = gt.entity_requirements.eligible_entities if gt.entity_requirements else []
        for item in [*gt.facts, *gt.rubrics, *entities]:
            if not set(item.evidence_ids) <= evidence_ids:
                raise ValueError("unknown evidence reference")
        fact_ids = {f.id for f in gt.facts}
        rubric_ids = {r.id for r in gt.rubrics}
        for check in self.evaluation_rule.checks:
            allowed = {
                "fact_match": fact_ids,
                "rubric_judge": rubric_ids,
                "entity_constraint": {"entities"} if gt.entity_requirements else set(),
                "citation_support": fact_ids | rubric_ids | ({"entities"} if entities else set()),
                "trace_assertion": fact_ids
                | rubric_ids
                | {"outcome"}
                | ({"entities"} if entities else set()),
            }[check.evaluator]
            if not set(check.target) <= allowed:
                raise ValueError(f"invalid target for {check.id}")
            if check.evaluator == "trace_assertion" and check.assertion is None:
                raise ValueError("trace checks require an assertion")
        return self

    def agent_input(self) -> dict:
        """Explicit allowlist: never serialize the complete case into a prompt."""
        return {
            "task": self.task.model_dump(mode="json"),
            "allowed_tools": self.environment.allowed_tools.copy(),
            "limits": self.environment.limits.model_dump(),
        }


class ToolEvent(Contract):
    tool: str
    arguments: dict[str, Any]
    started_at: AwareDatetime
    duration_ms: float = Field(ge=0)
    artifact_ids: list[str] = Field(default_factory=list)
    response: Any = None
    error: str | None = None


class BenchmarkRun(Contract):
    case_id: str
    case_revision: int = Field(gt=0)
    snapshot_id: str
    agent_version: str
    model_config_data: dict[str, Any]
    evaluator_version: str
    final_answer: str
    outcome: Outcome
    tool_trace: list[ToolEvent]
    run_status: Literal["completed", "budget_exceeded", "agent_error"]
    latency_ms: float = Field(ge=0)
    tool_calls: int = Field(ge=0)
    token_usage: dict[str, int] = Field(default_factory=dict)


class CheckResult(Contract):
    check_id: str
    score: Score
    reason: str
    evidence_refs: list[str] = Field(default_factory=list)


class EvaluationResult(Contract):
    case_id: str
    check_results: list[CheckResult]
    dimension_scores: dict[Dimension, Score] = Field(default_factory=dict)
    total_score: Score | None = None
    passed: bool | None = None
    grading_status: Literal["completed", "evaluation_error", "invalid_case"]
    error: str | None = None
