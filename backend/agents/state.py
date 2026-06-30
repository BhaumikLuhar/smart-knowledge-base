from typing import TypedDict


class TraceEntry(TypedDict):
    """
    One execution step recorded by an agent.

    The trace is primarily used for:

    - debugging
    - observability
    - future UI reasoning display
    """

    agent_name: str
    input_summary: str
    output_summary: str
    latency: float


class AgentState(TypedDict):
    """
    Shared state flowing through the LangGraph workflow.

    Each agent receives this state,
    modifies only the fields it owns,
    and returns the updated state.

    Flow

    Planner
        ↓
    Research
        ↓
    Response
    """

    #
    # Incoming request
    #
    query: str
    session_id: str
    user_context: dict

    #
    #planner output
    #
    retrieval_strategy: str
    search_queries: list[str]

    #
    # Research output
    #
    retrieved_chunks: list[dict]
    no_results: bool

    #
    # Response output
    #
    answer: str
    citations: list[dict]
    confidence: float

    #
    #execution trace
    #
    trace: list[TraceEntry]