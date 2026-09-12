from tools.recharge import recharge
from tools.registry import ToolRegistry
from tools.rest import rest
from tools.search_knowledge import search_knowledge
from tools.work import work


class ExecutorAgent:
    def __init__(self, name="ExecutorAgent"):
        self.name = name
        self.tool_registry = ToolRegistry()

        self.tool_registry.register("work", work)
        self.tool_registry.register("recharge", recharge)
        self.tool_registry.register("rest", rest)
        self.tool_registry.register("search_knowledge", search_knowledge)

        self.results = []

    def execute_step(self, step, agent):
        """
        Executes a single step of the plan.
        """
        action = step.get("action")

        if action not in self.tool_registry.list_tools():
            return{
                "success": False,
                "action": action,
                "error": "Unknown tool"
            }

        try:
            result = self.tool_registry.execute(action, agent)
            execution_result = {
                "success": True,
                "action": action,
                "result": result
            }
            self.results.append(execution_result)
            return execution_result
        except ValueError as e:
            execution_result = {
                "success": False,
                "action": action,
                "error": str(e)
            }
            self.results.append(execution_result)
            return execution_result

    def execute_plan(self, plan, agent):
        """
        Executes a sequence of steps in the plan.
        """
        self.results = []

        for step in plan:
            result = self.execute_step(step, agent)
            if not result["success"]:
                break

        return self.results