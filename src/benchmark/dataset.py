"""Local dataset loading and integrity-checked snapshot retrieval. No network fallback."""

import hashlib
import json
from pathlib import Path
from typing import Any

from pydantic import AwareDatetime, Field, model_validator

from benchmark.models import BenchmarkCase, Contract


class Artifact(Contract):
    id: str
    url: str
    path: str
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    captured_at: AwareDatetime


class Fault(Contract):
    id: str
    tool: str
    arguments: dict[str, Any]
    trigger_calls: list[int] = Field(min_length=1)
    error: str
    response: Any = None

    @model_validator(mode="after")
    def positive_calls(self):
        if any(n < 1 for n in self.trigger_calls) or len(set(self.trigger_calls)) != len(
            self.trigger_calls
        ):
            raise ValueError("fault call indices must be positive and unique")
        return self


class SnapshotManifest(Contract):
    id: str
    synthetic: bool
    artifacts: list[Artifact]
    faults: list[Fault] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_ids(self):
        for items in (self.artifacts, self.faults):
            ids = [item.id for item in items]
            if len(ids) != len(set(ids)):
                raise ValueError("duplicate manifest ID")
        return self


def load_case(path: Path) -> BenchmarkCase:
    # JSON is also a YAML 1.2 subset; YAML-only syntax is intentionally not accepted.
    return BenchmarkCase.model_validate_json(path.read_text(encoding="utf-8"))


class SnapshotStore:
    def __init__(self, manifest_path: Path):
        self.root = manifest_path.parent.resolve()
        self.manifest = SnapshotManifest.model_validate_json(manifest_path.read_text("utf-8"))
        self.contents: dict[str, str] = {}
        for artifact in self.manifest.artifacts:
            path = (self.root / artifact.path).resolve()
            if not path.is_relative_to(self.root):
                raise ValueError("artifact path escapes snapshot directory")
            content = path.read_bytes()
            if hashlib.sha256(content).hexdigest() != artifact.sha256:
                raise ValueError(f"snapshot hash mismatch: {artifact.id}")
            self.contents[artifact.id] = content.decode("utf-8")

    def validate_case(self, case: BenchmarkCase) -> None:
        if case.environment.mode != "snapshot":
            raise ValueError("v1 supports snapshot cases only")
        if case.environment.snapshot_id != self.manifest.id:
            raise ValueError("snapshot ID mismatch")
        artifacts = {a.id: a for a in self.manifest.artifacts}
        for evidence in case.ground_truth.evidence:
            artifact = artifacts.get(evidence.artifact_id)
            if (
                artifact is None
                or artifact.url != evidence.url
                or artifact.captured_at != evidence.captured_at
            ):
                raise ValueError(f"evidence does not match artifact: {evidence.id}")
        fault_id = case.environment.fault_scenario_id
        if fault_id and fault_id not in {f.id for f in self.manifest.faults}:
            raise ValueError("unknown fault scenario")

    def fetch(self, url: str) -> dict[str, str]:
        return {a.id: self.contents[a.id] for a in self.manifest.artifacts if a.url == url}

    def search(self, query: str) -> dict[str, str]:
        """Small fixture search: case-insensitive token overlap, not a golden query replay."""
        tokens = set(query.casefold().split())
        ranked = []
        for artifact in self.manifest.artifacts:
            content = self.contents[artifact.id]
            haystack = f"{artifact.url} {content}".casefold()
            score = sum(token in haystack for token in tokens)
            if score:
                ranked.append((score, artifact.id, content))
        return {key: content for _, key, content in sorted(ranked, key=lambda r: (-r[0], r[1]))}


class FaultSession:
    """Create one per run. Counters apply only to matching tool/argument calls."""

    def __init__(self, fault: Fault):
        self.fault = fault
        self.matches = 0

    def intercept(self, tool: str, arguments: dict[str, Any]) -> dict | None:
        if tool != self.fault.tool or arguments != self.fault.arguments:
            return None
        self.matches += 1
        if self.matches in self.fault.trigger_calls:
            return {"error": self.fault.error, "response": self.fault.response}
        return None


def export_schema(path: Path) -> None:
    path.write_text(json.dumps(BenchmarkCase.model_json_schema(), indent=2) + "\n", "utf-8")
