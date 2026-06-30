from abc import ABC
from abc import abstractmethod

from agents.state import AgentState


class Agent(ABC):
    """
    Base interface for every workflow agent.

    Every agent receives the shared AgentState,
    performs one responsibility,
    and returns the updated state.

    Agents should only modify the fields they own.
    """

    #
    # Human-readable identifier.
    #
    name: str

    @abstractmethod
    async def execute(
        self,
        state: AgentState,
    ) -> AgentState:
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
        raise NotImplementedError