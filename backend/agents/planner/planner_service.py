from agents.planner.planner_agent import PlannerAgent
from agents.state import AgentState

from core.auth.user_context import UserContext


class PlannerService:
    """
    Executes only the Planner agent.

    Used for:

    - debugging
    - development
    - /chat/plan endpoint

    This service intentionally bypasses the
    complete workflow and executes only the
    first agent.
    """

    def __init__(self):

        self.agent = PlannerAgent()

    async def plan(
        self,
        *,
        query: str,
        user_context: UserContext,
        session_id: str = "",
    ) -> AgentState:

        state: AgentState = {
            "query": query,
            "session_id": session_id,
            "user_context": vars(user_context),
            "retrieval_strategy": "",
            "search_queries": [],
            "retrieved_chunks": [],
            "no_results": False,
            "answer": "",
            "citations": [],
            "confidence": 0.0,
            "trace": [],
            "tokens_used": 0,
        }

        return await self.agent.execute(state)