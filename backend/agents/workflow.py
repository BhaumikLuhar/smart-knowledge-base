from langgraph.graph import (
    START,
    END,
    StateGraph,
)

from agents.state import AgentState

from agents.planner.planner_agent import PlannerAgent
from agents.research.research_agent import ResearchAgent
from agents.response.response_agent import ResponseAgent

from core.auth.user_context import UserContext

from core.retrieval.retrieval_pipeline import RetrievalPipeline


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

        workflow = StateGraph(AgentState)

        #
        # Nodes
        #
        workflow.add_node(
            "planner",
            PlannerAgent().execute,
        )

        self.research_agent = ResearchAgent(
            pipeline=self.pipeline,
        )

        workflow.add_node(
            "research",
            self.research_agent.execute,
        )

        workflow.add_node(
            "response",
            ResponseAgent().execute,
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

        initial_state: AgentState = {
            #
            # Request
            #
            "query": query,
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
            # Response
            #
            "answer": "",

            "citations": [],

            "confidence": 0.0,

            #
            # Trace
            #
            "trace": [],
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