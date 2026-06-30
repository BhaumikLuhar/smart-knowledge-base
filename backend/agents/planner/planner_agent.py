import json
import re
import time

from agents.base_agent import Agent
from agents.state import AgentState

from core.generation.llm_provider import get_llm
from core.generation.prompts import (
    PLANNER_SYSTEM_PROMPT_V1,
)


class PlannerAgent(Agent):
    """
    Entry point of the agent workflow.

    Responsibilities
    ----------------
    - Understand the user's request
    - Decide retrieval strategy
    - Generate search queries
    """

    name="planner"

    VALID_STRATEGIES = {"direct", "multi_step", "summary"}


    @staticmethod
    def _strip_json_fences(text: str)-> str:
        """
        Remove Markdown code fences if the model
        accidentally returns them.
        """

        text = text.strip()

        text= re.sub(
            r"^```(?:json)?",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text= re.sub(
            r"```$",
            "",
            text,
        )

        return text.strip()
    

    @classmethod
    def _fallback(
        cls,
        state: AgentState,
    )-> AgentState:
        """
        Fallback strategy if the model fails to return valid JSON.
        """

        state["retrieval_strategy"] = "direct"
        state["search_queries"] = [state["query"]]

        return state
    

    async def execute(
            self,
            state: AgentState,
    )-> AgentState:
        """
        Execute one workflow step.

        Parameters
        ----------
        state
            Current workflow state.

        Returns
        -------
        AgentState
            Updated workflow state.
        """

        start = time.perf_counter()

        system_message = {
            "role": "system",
            "content": PLANNER_SYSTEM_PROMPT_V1,
        }


        user_message = {
            "role": "user",
            "content": state["query"],
        }

        try:
            response, _ = get_llm().generate(
                [
                    system_message,
                    user_message,
                ]
            )

            cleaned= self._strip_json_fences(response)

            result= json.loads(cleaned)

            strategy= result.get("strategy","direct")

            queries= result.get("queries",[])

            # Validate strategy
            if strategy not in self.VALID_STRATEGIES:
                raise ValueError(
                    f"Invalid strategy: {strategy}. "
                    f"Must be one of {self.VALID_STRATEGIES}"
                )
            
            if not isinstance(queries, list):
                raise ValueError(
                    f"Invalid queries: {queries}. "
                    f"Must be a list of strings."
                )
            
            queries = [
                q.strip()
                for q in queries
                if isinstance(q, str)
                and q.strip()
            ]

            if not queries:
                raise ValueError(
                    "No valid search queries."
                )

            state["retrieval_strategy"] = strategy

            state["search_queries"] = queries[:3]

        except Exception:

            #
            # Never fail the workflow because
            # of Planner output.
            #
            #
            # TODO (Day 19):
            # Record planner failures in metrics.
            #
            state = self._fallback(state)

        latency = (
            time.perf_counter() - start
        ) * 1000

        state["trace"].append(
            {
                "agent_name": self.name,
                "input_summary": state["query"][:100],
                "output_summary": (
                    f"strategy={state['retrieval_strategy']}, "
                    f"queries={state['search_queries']}"
                ),
                "latency": round(
                    latency,
                    2,
                ),
            }
        )

        return state