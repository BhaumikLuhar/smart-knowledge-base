import time

from agents.base_agent import Agent
from agents.state import AgentState


class ResearchAgent(Agent):
    """
    Temporary Research Agent.

    Day 15:
        Stub implementation.

    Day 16:
        Executes RetrievalPipeline and aggregates
        authorized chunks.
    """

    name = "research"

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
                    f"{len(state['search_queries'])} queries"
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