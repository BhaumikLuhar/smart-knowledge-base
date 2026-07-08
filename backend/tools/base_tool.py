from abc import ABC
from abc import abstractmethod
from typing import Any


class Tool(ABC):
    """
    Base interface for workflow tools.

    Tools provide reusable functionality that agents
    can invoke without knowing the concrete implementation.
    """

    #
    # Human-readable identifier.
    #
    name: str

    @abstractmethod
    def execute(
        self,
        payload: dict[str, Any],
    ) -> Any:
        """
        Execute the tool.

        Parameters
        ----------
        payload
            Input parameters required by the tool.

        Returns
        -------
        Any
            Tool-specific result.
        """
        raise NotImplementedError