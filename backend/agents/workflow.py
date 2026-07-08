from langgraph.graph import (
    START,
    END,
    StateGraph,
)

from agents.state import AgentState

from agents.registry import (
    get_agent,
    register_agent,
)

from agents.planner.planner_agent import PlannerAgent
from agents.research.research_agent import ResearchAgent
from agents.response.response_agent import ResponseAgent

from core.auth.user_context import UserContext

from core.retrieval.retrieval_pipeline import RetrievalPipeline

from core.memory.session_memory import SessionMemory

from core.conversation.query_resolver import QueryResolver

#
# Built-in workflow agents.
#

register_agent(
    "planner",
    PlannerAgent,
)

register_agent(
    "research",
    ResearchAgent,
)

register_agent(
    "response",
    ResponseAgent,
)


class AgentWorkflow:
    """
    Singleton LangGraph workflow.

    The workflow is compiled once and reused
    for every request.
    """

    _instance = None

    @classmethod
    def get_instance(
        cls,
        pipeline: RetrievalPipeline,
    ):

        if cls._instance is None:
            cls._instance = cls(
                pipeline=pipeline,
            )

        return cls._instance

    def __init__(self, pipeline: RetrievalPipeline = None):

        if hasattr(self, "graph"):
            return
        
        self.pipeline = pipeline
        self.memory = SessionMemory(pipeline.sql_store)
        self.query_resolver = QueryResolver()

        workflow = StateGraph(AgentState)

        #
        # Nodes
        #
        planner_class = get_agent("planner")
        self.planner_agent = planner_class(
            self.pipeline.sql_store,
        )

        workflow.add_node(
            "planner",
            self.planner_agent.execute,
        )

        research_class = get_agent("research")
        self.research_agent = research_class(
            pipeline=self.pipeline,
        )

        workflow.add_node(
            "research",
            self.research_agent.execute,
        )

        response_class = get_agent("response")
        self.response_agent = response_class(
            self.pipeline.sql_store,
        )

        workflow.add_node(
            "response",
            self.response_agent.execute,
        )

        #
        # Edges
        #
        workflow.add_edge(
            START,
            "planner",
        )

        workflow.add_edge(
            "planner",
            "research",
        )

        workflow.add_edge(
            "research",
            "response",
        )

        workflow.add_edge(
            "response",
            END,
        )

        self.graph = workflow.compile()

    async def run(
        self,
        *,
        query: str,
        user_context: UserContext,
        session_id: str,
    ) -> AgentState:
        """
        Execute the complete agent pipeline.
        """

        history = await self.memory.get_session_history(
            session_id=session_id,
        )

        resolved_query = self.query_resolver.resolve(
            query=query,
            history=history,
        )

        initial_state: AgentState = {
            #
            # Request
            #
            "query": query,
            "resolved_query": resolved_query,
            "session_id": session_id,
            "user_context": vars(user_context),

            #
            # Planner
            #
            "retrieval_strategy": "",

            "search_queries": [],

            #
            # Research
            #
            "retrieved_chunks": [],

            "no_results": False,

            #
            # Conversation memory
            #
            "history": history,

            #
            # Response
            #
            "answer": "",

            "citations": [],

            #
            # Confidence
            #
            "confidence_score": 0.0,

            "confidence_level": "low",

            #
            # Trace
            #
            "trace": [],

            "tokens_used": 0,

            "planner_tokens_used": 0,
        }

        result = await self.graph.ainvoke(
            initial_state
        )

        return result


async def run_agent_pipeline(
    *,
    query: str,
    user_context: UserContext,
    session_id: str,
    pipeline: RetrievalPipeline,
) -> AgentState:
    """
    Public helper used by ChatService.

    ChatService should never know anything
    about LangGraph internals.
    """

    return await AgentWorkflow.get_instance(pipeline=pipeline).run(
        query=query,
        user_context=user_context,
        session_id=session_id,
    )