import json
import re
import time

from agents.base_agent import Agent
from agents.state import AgentState

from core.generation.llm_provider import get_llm
from core.generation.prompts import (
    PLANNER_SYSTEM_PROMPT_V1,
)

from storage.sql.sql_store import SQLStore

from core.observability.collector import (
    ObservabilityCollector,
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

    def __init__(self,sql_store: SQLStore):
        self.metrics = ObservabilityCollector(
            sql_store
        )

    @staticmethod
    def _determine_strategy(
        query: str,
        llm_strategy: str,
    ) -> str:
        """
        Apply deterministic overrides for
        obvious query patterns.

        The LLM still determines the strategy
        for ambiguous queries, while simple
        cases are handled deterministically.
        """

        query = query.lower()

        #
        # Summary requests
        #
        if any(
            keyword in query
            for keyword in (
                "summarize",
                "summary",
                "overview",
                "brief",
            )
        ):
            return "summary"

        #
        # Multi-step requests
        #
        if any(
            keyword in query
            for keyword in (
                "compare",
                "comparison",
                "difference",
                "differences",
                "versus",
                "vs",
                "both",
            )
        ):
            return "multi_step"

        #
        # Otherwise trust the LLM
        #
        return llm_strategy


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
        state["search_queries"] = [state["resolved_query"]]

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
            "content": state["resolved_query"],
        }

        try:
            response, planner_tokens = get_llm().generate(
                [
                    system_message,
                    user_message,
                ]
            )

            state["planner_tokens_used"] = planner_tokens

            cleaned= self._strip_json_fences(response)

            result= json.loads(cleaned)

            llm_strategy = result.get(
                "strategy",
                "direct",
            )

            strategy = self._determine_strategy(
                state["resolved_query"],
                llm_strategy,
            )

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

        except Exception as e:

            latency = (
                time.perf_counter() - start
            ) * 1000

            await self.metrics.record_agent_failure(
                user_id=state["user_context"]["id"],
                agent_name=self.name,
                latency=latency,
                error_message=str(e),
            )
            state = self._fallback(state)

        latency = (
            time.perf_counter() - start
        ) * 1000

        state["trace"].append(
            {
                "agent_name": self.name,
                "input_summary": (
                    f"query={state['query'][:40]} | "
                    f"resolved={state['resolved_query'][:40]}"
                ),
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

        await self.metrics.record_agent_success(
            user_id=state["user_context"]["id"],
            agent_name=self.name,
            latency=latency,
            tokens=planner_tokens,
        )

        return state