import time

from agents.base_agent import Agent
from agents.state import AgentState

from core.auth.user_context import UserContext
from core.generation.generator import Generator


class ResponseAgent(Agent):
    """
    Final agent in the LangGraph workflow.

    Responsibilities
    ----------------
    - Handle no-results without calling the LLM.
    - Delegate grounded answer generation to Generator.
    - Populate the final AgentState.
    - Record execution trace.
    """

    name = "response"

    def __init__(self):
        self.generator = Generator()

    async def execute(
        self,
        state: AgentState,
    ) -> AgentState:

        start = time.perf_counter()

        #
        # Never call the LLM without retrieval context.
        #
        if (
            state.get("no_results")
            or not state["retrieved_chunks"]
        ):

            state["answer"] = Generator.FALLBACK_MESSAGE
            state["citations"] = []
            state["confidence_score"] = 0.0
            state["confidence_level"] = "low"
            state["tokens_used"] = 0

            latency = (
                time.perf_counter() - start
            ) * 1000

            state["trace"].append(
                {
                    "agent_name": self.name,
                    "input_summary": "0 retrieved chunks",
                    "output_summary": "fallback response",
                    "latency": round(latency, 2),
                }
            )

            return state
        
        user_context = UserContext(**state["user_context"])

        response = self.generator.generate_response(
            query=state["query"],
            chunks=state["retrieved_chunks"],
            user_context=user_context,
            history=state.get("history", []),
        )

        state["answer"] = response.answer
        state["citations"] = response.citations
        state["confidence_score"] = response.confidence_score
        state["confidence_level"] = response.confidence_level
        state["tokens_used"] = response.tokens_used


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
                    f"answer={len(response.answer)} chars, "
                    f"citations={len(response.citations)}, "
                    f"confidence={response.confidence_level}, "
                    f"tokens={response.tokens_used}"
                ),
                "latency": round(latency, 2),
            }
        )

        return state