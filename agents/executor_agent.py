from core.logger import logger
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
        Executes a single step, records its outcome,
        and stores the experience in memory.
        """
        action = step.get("action")

        if action not in self.tool_registry.list_tools():
            return {
                "success": False,
                "action": action,
                "error": "Unknown tool",
            }

        try:
            result = self.tool_registry.execute(action, agent)

            execution_result = {
                "success": True,
                "action": action,
                "result": result,
            }

        except Exception as e:  # noqa: BLE001
            logger.exception("Tool execution failed: %s", action)

            execution_result = {
                "success": False,
                "action": action,
                "error": str(e),
            }

        self.results.append(execution_result)

        # Record the outcome in the agent's experience memory.
        try:
            memory_manager = getattr(agent, "memory_manager", None)

            if memory_manager is not None:
                experience = {
                    "goal": getattr(agent, "goal", ""),
                    "action": action,
                    "result": str(
                        execution_result.get(
                            "result",
                            execution_result.get("error", "")
                        )
                    ),
                    "success": execution_result["success"],
                }

                if hasattr(agent, "energy"):
                    experience["energy"] = agent.energy

                if not execution_result["success"]:
                    experience["error"] = execution_result.get(
                        "error", "Unknown error"
                    )

                memory_manager.record_experience(experience)

        except Exception:  # noqa: BLE001
            logger.exception("Failed to record execution experience")

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

        return {
            "success": self.evaluate_results(),
            "results": self.results
        }

    def evaluate_results(self):
        """
        Evaluates the results of the executed plan.
        """
        if not self.results:
            return False # No results to evaluate

        for result in self.results:
            if not result.get("success", False):
                return False # If any step failed, the overall result is a failure

        return True # All steps succeeded