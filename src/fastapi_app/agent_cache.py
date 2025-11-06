"""
agent_cache.py

Caches and reuses MI agents to avoid recreating them on every request.
"""

from typing import Optional, Callable
from agents import Agent  # import directly from agents, not from custom_agents

# Cached base agent
base_agent: Optional[Agent] = None

# Function pointer for creating agents (set later)
_create_agent_fn: Optional[Callable[..., Agent]] = None


def register_create_agent(fn: Callable[..., Agent]) -> None:
    """
    Registers the create_agent function to avoid circular imports.
    Must be called once (e.g. at module import in custom_agents.py).
    """
    global _create_agent_fn
    _create_agent_fn = fn


def get_or_create_agent(
    use_harm_guardrail: bool = True,
    use_mi_check_guardrail: bool = True,
    use_sensing_agent: bool = False,
) -> Agent:
    """
    Returns an MI Agent.

    - Reuses the cached base agent if no guardrails or tools are requested.
    - Creates a new one otherwise.
    """
    global base_agent, _create_agent_fn

    if _create_agent_fn is None:
        raise RuntimeError("create_agent function not registered in agent_cache")

    # Create a fresh agent if any of these flags are True
    if use_harm_guardrail or use_mi_check_guardrail or use_sensing_agent:
        print("Creating new agent with custom settings")
        return _create_agent_fn(
            use_harm_guardrail=use_harm_guardrail,
            use_mi_check_guardrail=use_mi_check_guardrail,
            use_sensing_agent=use_sensing_agent,
        )

    # Reuse or lazily create the base agent
    if base_agent is None:
        print("Creating and caching base agent")
        base_agent = _create_agent_fn(
            use_harm_guardrail=False,
            use_mi_check_guardrail=False,
            use_sensing_agent=False,
        )
    return base_agent
