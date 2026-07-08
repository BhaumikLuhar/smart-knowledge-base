from typing import Type

from agents.base_agent import Agent

AGENT_REGISTRY: dict[str, Type[Agent]] = {}


def register_agent(
    name: str,
    agent_class: Type[Agent],
) -> None:
    """
    Register an agent implementation.
    """

    AGENT_REGISTRY[name] = agent_class


def get_agent(
    name: str,
) -> Type[Agent]:
    """
    Return a registered agent class.
    """

    agent_class = AGENT_REGISTRY.get(name)

    if agent_class is None:
        raise ValueError(
            f"Agent '{name}' is not registered."
        )

    return agent_class