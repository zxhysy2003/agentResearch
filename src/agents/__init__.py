"""Load the service registry only when a public registry export is requested."""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agents.agents import (
        DEFAULT_AGENT,
        AgentGraph,
        AgentGraphLike,
        get_agent,
        get_all_agent_info,
        load_agent,
    )

__all__ = [
    "get_agent",
    "load_agent",
    "get_all_agent_info",
    "DEFAULT_AGENT",
    "AgentGraph",
    "AgentGraphLike",
]


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module("agents.agents"), name)
    globals()[name] = value
    return value
