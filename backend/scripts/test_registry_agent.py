from agents.registry import (
    get_agent,
    register_agent,
)

from agents.base_agent import Agent
from agents.state import AgentState


class DummyAgent(Agent):

    name = "dummy"

    async def execute(
        self,
        state: AgentState,
    ) -> AgentState:
        return state


register_agent(
    "dummy",
    DummyAgent,
)

assert get_agent("dummy") is DummyAgent

print("✓ Agent registry extension test passed")