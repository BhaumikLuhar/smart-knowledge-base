import time

from agents.base_agent import Agent
from agents.state import AgentState


class ResponseAgent(Agent):
    """
    Temporary Response Agent.

    Day 15:
        Stub implementation.

    Day 17:
        Generates the final grounded answer.
    """

    name = "response"

    async def execute(
        self,
        state: AgentState,
    ) -> AgentState:

        start = time.perf_counter()

        latency = (
            time.perf_counter() - start
        ) * 1000

        state["trace"].append(
            {
                "agent_name": self.name,
                "input_summary": (
                    f"{len(state['retrieved_chunks'])} chunks"
                ),
                "output_summary": (
                    "stub"
                ),
                "latency": round(
                    latency,
                    2,
                ),
            }
        )

        return state