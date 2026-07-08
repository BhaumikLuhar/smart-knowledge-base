from typing import Type

from tools.base_tool import Tool


TOOL_REGISTRY: dict[str, Type[Tool]] = {}


def register_tool(
    name: str,
    tool_class: Type[Tool],
) -> None:
    """
    Register a tool implementation.
    """

    TOOL_REGISTRY[name] = tool_class


def get_tool(
    name: str,
) -> Tool:
    """
    Create a tool instance.

    Raises
    ------
    ValueError
        If the requested tool has not been registered.
    """

    tool_class = TOOL_REGISTRY.get(name)

    if tool_class is None:
        raise ValueError(
            f"Tool '{name}' is not registered."
        )

    return tool_class()