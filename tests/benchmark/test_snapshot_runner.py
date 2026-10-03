"""Synthetic model responses exercise the runner; they are not capability scores."""

import asyncio
import copy
import json
from unittest.mock import patch

import pytest
from langchain_core.language_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolCall, ToolMessage
from pydantic import Field

from benchmark.dataset import Fault, SnapshotStore, load_case
from benchmark.runner import (
    DEFAULT_CASES,
    DEFAULT_MANIFEST,
    MODEL_CONFIG,
    deepseek_factory,
    load_dataset,
    run_case,
    run_dataset,
)
from benchmark.tools import PAGE_SIZE, SnapshotTools


class ScriptedModel(FakeMessagesListChatModel):
    seen: list[list[BaseMessage]] = Field(default_factory=list)
    bound_names: list[str] = Field(default_factory=list)
    delay: float = 0

    def bind_tools(self, tools, **kwargs):
        self.bound_names = [tool.name for tool in tools]
        return self

    async def ainvoke(self, input, config=None, **kwargs):
        self.seen.append(list(input))
        await asyncio.sleep(self.delay)
        return await super().ainvoke(input, config=config, **kwargs)


def final(text="Synthetic test answer", **kwargs):
    return AIMessage(
        content=json.dumps({"answer": text, "outcome": "answered"}),
        usage_metadata={"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
        **kwargs,
    )


def calls(*requests):
    return AIMessage(
        content="",
        tool_calls=[
            ToolCall(name=name, args=args, id=f"call-{index}")
            for index, (name, args) in enumerate(requests)
        ],
        usage_metadata={"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
    )


@pytest.fixture
def store():
    return SnapshotStore(DEFAULT_MANIFEST)


@pytest.fixture
def case():
    return load_case(DEFAULT_CASES / "github_lookup_04.json")


@pytest.fixture
def adapter(store):
    return SnapshotTools(store)


def test_all_snapshot_resources_and_pagination(adapter, store):
    for artifact in store.manifest.artifacts:
        url = artifact.url
        if "raw.githubusercontent.com" in url:
            repository = "/".join(url.split("/")[3:5])
            resource, path = "file", "README.md"
        else:
            repository = "/".join(url.split("/")[4:6])
            resource = (
                "latest_release"
                if "/releases/" in url
                else ("issues" if "/issues?" in url else "repository")
            )
            path = None
        offset = 0
        body = ""
        while True:
            result = adapter.github_read(repository, resource, path=path, offset=offset)
            assert result["status"] == "ok"
            page = result["results"][0]
            assert page["artifact_id"] == artifact.id
            assert page["url"] == url
            assert page["synthetic"] is False
            assert len(page["content"]) <= PAGE_SIZE
            assert adapter.fetch_page(url, offset)["results"][0] == page
            body += page["content"]
            if page["next_offset"] is None:
                break
            offset = page["next_offset"]
        assert body == store.contents[artifact.id]


def test_search_is_bounded_and_reads_never_fall_back_to_network(adapter):
    with patch("httpx.Client.request", side_effect=AssertionError("no network")):
        results = adapter.web_search("github")
        assert len(results["results"]) == 5
        assert all(len(hit["snippet"]) <= 500 for hit in results["results"])
        assert all("content" not in hit for hit in results["results"])
        assert adapter.fetch_page("https://unknown.invalid")["status"] == "not_found"
        assert adapter.github_read("missing/project")["status"] == "not_found"
        assert adapter.web_search("xyz-nonexistent-token")["results"] == []
    with pytest.raises(ValueError, match="relative"):
        adapter.github_read("owner/repo", "file", path="../review.json")
    with pytest.raises(ValueError, match="non-negative"):
        adapter.fetch_page("https://unknown.invalid", offset=-1)
    with pytest.raises(ValueError, match="exceeds"):
        adapter.fetch_page(results["results"][0]["url"], offset=10**9)
    with pytest.raises(ValueError):
        adapter.bindable_tools(["web_search", "write_file"])


@pytest.mark.asyncio
async def test_native_loop_evidence_is_public_and_tool_ids_are_preserved(case, store):
    case.environment.allowed_tools = ["github_read"]
    model = ScriptedModel(
        responses=[
            calls(
                (
                    "github_read",
                    {"repository": "browser-use/browser-use", "resource": "latest_release"},
                )
            ),
            final(
                "Synthetic [source](https://api.github.com/repos/browser-use/browser-use/releases/latest)"
            ),
        ]
    )
    result = await run_case(case, store, model, agent_version="fixture", model_config={})
    assert result.run.run_status == "completed"
    assert result.run.tool_calls == 1
    assert result.run.token_usage["total_tokens"] == 30
    assert result.run.tool_trace[0].artifact_ids == ["latest_browser"]
    assert model.bound_names == ["github_read"]
    public_text = str(model.seen[0])
    for forbidden in ("ground_truth", "evaluation_rule", "e_1", "0.13.10"):
        assert forbidden not in public_text
    response = next(message for message in model.seen[1] if isinstance(message, ToolMessage))
    assert response.tool_call_id == "call-0"
    assert "0.13.10" in response.content


@pytest.mark.asyncio
async def test_multicall_budget_never_dispatches_excess_calls(case, store):
    case.environment.limits.max_tool_calls = 1
    model = ScriptedModel(
        responses=[
            calls(
                ("github_read", {"repository": "fastapi/fastapi"}),
                ("github_read", {"repository": "qdrant/qdrant"}),
            )
        ]
    )
    result = await run_case(case, store, model, agent_version="fixture", model_config={})
    assert result.run.run_status == "budget_exceeded"
    assert result.run.tool_calls == len(result.run.tool_trace) == 1
    assert result.run.tool_trace[0].artifact_ids == ["repo_fastapi"]
    assert len([message for message in result.messages if isinstance(message, ToolMessage)]) == 1
    assert "budget exhausted" in result.error


@pytest.mark.asyncio
async def test_failed_tools_count_and_model_can_recover(case, store):
    model = ScriptedModel(
        responses=[
            calls(
                ("delete_repository", {"repository": "fastapi/fastapi"}),
                ("github_read", {"repository": "not-a-repository"}),
                ("fetch_page", {"url": "https://missing.invalid"}),
            ),
            final(),
        ]
    )
    result = await run_case(case, store, model, agent_version="fixture", model_config={})
    assert result.run.run_status == "completed"
    assert result.run.tool_calls == 3
    assert all(event.error for event in result.run.tool_trace)
    assert len([message for message in model.seen[1] if isinstance(message, ToolMessage)]) == 3


@pytest.mark.asyncio
async def test_timeout_and_invalid_final_are_distinct_failures(case, store):
    case.environment.limits.timeout_seconds = 0.01
    result = await run_case(
        case,
        store,
        ScriptedModel(responses=[final()], delay=0.05),
        agent_version="fixture",
        model_config={},
    )
    assert result.run.run_status == "budget_exceeded"
    assert result.run.token_usage == {}
    case.environment.limits.timeout_seconds = 1
    result = await run_case(
        case,
        store,
        ScriptedModel(responses=[AIMessage(content="not JSON")]),
        agent_version="fixture",
        model_config={},
    )
    assert result.run.run_status == "agent_error"
    assert result.run.final_answer == "not JSON"
    assert result.error


@pytest.mark.asyncio
async def test_missing_usage_is_not_reported_as_zero(case, store):
    result = await run_case(
        case,
        store,
        ScriptedModel(responses=[AIMessage(content=final().content)]),
        agent_version="fixture",
        model_config={},
    )
    assert result.run.run_status == "completed"
    assert result.run.token_usage == {}


@pytest.mark.asyncio
async def test_faults_reset_per_run_and_recovery_is_observable(case, store):
    arguments = {"repository": "fastapi/fastapi"}
    store.manifest.faults = [
        Fault(
            id="once", tool="github_read", arguments=arguments, trigger_calls=[1], error="timeout"
        )
    ]
    case.environment.fault_scenario_id = "once"
    for _ in range(2):
        model = ScriptedModel(
            responses=[
                calls(("github_read", arguments)),
                calls(("github_read", arguments)),
                final(),
            ]
        )
        result = await run_case(case, store, model, agent_version="fixture", model_config={})
        assert result.run.run_status == "completed"
        assert result.run.tool_calls == 2
        assert result.run.tool_trace[0].error == "timeout"
        assert result.run.tool_trace[1].error is None
        assert result.run.tool_trace[1].artifact_ids == ["repo_fastapi"]


@pytest.mark.asyncio
async def test_deadline_preserves_interrupted_tool_event(case, store):
    case.environment.limits.timeout_seconds = 0.05
    model = ScriptedModel(responses=[calls(("github_read", {"repository": "fastapi/fastapi"}))])

    async def slow_tool(*args, **kwargs):
        await asyncio.sleep(1)

    with patch("langchain_core.tools.StructuredTool.ainvoke", new=slow_tool):
        result = await run_case(case, store, model, agent_version="fixture", model_config={})
    assert result.run.run_status == "budget_exceeded"
    assert result.run.tool_calls == 1
    assert "interrupted" in result.run.tool_trace[0].error
    assert result.run.tool_trace[0].duration_ms > 0


@pytest.mark.asyncio
async def test_dataset_repeats_have_fresh_sessions_and_one_error_does_not_stop_batch(tmp_path):
    models = []

    def factory():
        index = len(models)
        responses = [AIMessage(content="synthetic invalid response")] if index == 0 else [final()]
        model = ScriptedModel(responses=copy.deepcopy(responses))
        models.append(model)
        return model

    summary = await run_dataset(
        output=tmp_path / "runs",
        repeat=2,
        model_factory=factory,
        model_config={"model": "synthetic-fixture"},
    )
    assert summary["total_runs"] == 20
    assert summary["run_failures"] == 1
    assert summary["ungraded_runs"] == 20
    assert summary["pass_rate_among_graded"] is None
    assert summary["grading_coverage"] == 0
    assert summary["total_tokens"] is None
    assert all(len(model.seen) == 1 and len(model.seen[0]) == 2 for model in models)
    assert all(len(model.bound_names) == 3 for model in models)
    assert (tmp_path / "runs/summary.md").exists()
    with pytest.raises(ValueError, match="already exists"):
        await run_dataset(output=tmp_path / "runs", model_factory=factory)


def test_preflight_rejects_duplicate_and_invalid_cases_without_model_calls(tmp_path):
    cases_dir = tmp_path / "cases"
    cases_dir.mkdir()
    raw = (DEFAULT_CASES / "github_lookup_01.json").read_bytes()
    (cases_dir / "one.json").write_bytes(raw)
    (cases_dir / "two.json").write_bytes(raw)
    with pytest.raises(ValueError, match="duplicate"):
        load_dataset(cases_dir, DEFAULT_MANIFEST)
    (cases_dir / "two.json").unlink()
    data = json.loads(raw)
    data["environment"]["allowed_tools"] = ["delete_repository"]
    (cases_dir / "one.json").write_text(json.dumps(data))
    with pytest.raises(ValueError, match="unsupported"):
        load_dataset(cases_dir, DEFAULT_MANIFEST)


def test_deepseek_profile_and_missing_credentials(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with patch("dotenv.load_dotenv"):
        with pytest.raises(ValueError, match="DEEPSEEK_API_KEY"):
            deepseek_factory("deepseek-flash")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "synthetic-test-key")
        model = deepseek_factory("deepseek-flash")()
    assert model.extra_body == {
        "thinking": {"type": "disabled"},
        "response_format": {"type": "json_object"},
    }
    assert model.temperature == MODEL_CONFIG["temperature"]
    assert model.max_retries == 0 and model.streaming is False
    assert "response_format" not in model.model_kwargs
