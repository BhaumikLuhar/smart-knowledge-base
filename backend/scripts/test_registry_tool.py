from tools.base_tool import Tool
from tools.registry import (
    get_tool,
    register_tool,
)


class DummyTool(Tool):
    """
    Simple test tool.
    """

    name = "dummy"

    def execute(
        self,
        payload: dict,
    ):
        return {
            "status": "ok",
            "payload": payload,
        }


register_tool(
    "dummy",
    DummyTool,
)

tool = get_tool("dummy")

result = tool.execute({})

assert result["status"] == "ok"

print("✓ Tool registry extension test passed")