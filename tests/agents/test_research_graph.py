from unittest.mock import AsyncMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage


@pytest.mark.asyncio
@pytest.mark.parametrize("unsafe", [True, False])
async def test_service_input_guard_still_precedes_model(monkeypatch, unsafe):
    from agents import research_assistant as module
    from agents.safeguard import SafeguardOutput, SafetyAssessment

    output = SafeguardOutput(
        safety_assessment=SafetyAssessment.UNSAFE if unsafe else SafetyAssessment.SAFE,
        unsafe_categories=["synthetic test"] if unsafe else [],
    )
    guard = AsyncMock(return_value=output)
    monkeypatch.setattr(module.Safeguard, "ainvoke", guard)
    model = AsyncMock(return_value=AIMessage(content="synthetic test answer"))
    monkeypatch.setattr(module, "wrap_model", lambda _: type("Bound", (), {"ainvoke": model})())
    monkeypatch.setattr(module, "get_model", lambda _: None)
    result = await module.research_assistant.ainvoke(
        {"messages": [HumanMessage(content="synthetic test input")]},
        {"configurable": {"model": "synthetic"}},
    )
    assert guard.await_count == 1
    assert model.await_count == (0 if unsafe else 1)
    assert len(result["messages"]) == 2
    if unsafe:
        assert "flagged" in result["messages"][-1].content
