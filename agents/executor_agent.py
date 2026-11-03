from core.logger import logger


class ExecutorAgent:

    def __init__(
        self,
        tool_execution_service=None,
        name="ExecutorAgent",
    ):
        self.name = name
        if tool_execution_service is None:
            from integrations.execution_service import ToolExecutionService
            from integrations.manager import MCPManager
            from tools.recharge import recharge
            from tools.registry import ToolRegistry
            from tools.rest import rest
            from tools.search_knowledge import search_knowledge
            from tools.work import work

            registry = ToolRegistry()
            registry.register("work", work)
            registry.register("recharge", recharge)
            registry.register("rest", rest)
            registry.register("search_knowledge", search_knowledge)

            mcp_manager = MCPManager(tool_registry=registry)

            tool_execution_service = ToolExecutionService(
                tool_registry=registry,
                mcp_manager=mcp_manager,
            )

        self.tool_execution_service = tool_execution_service
        self.results = []

    async def execute_step(self, step, agent):
        """
        Executes one local or MCP tool and records its outcome.
        """

        action = step.get("action")
        arguments = step.get("arguments", {})

        if not action:
            return {
                "success": False,
                "action": action,
                "error": "Missing tool action",
            }

        try:
            result = await self.tool_execution_service.execute(
                tool_name=action,
                agent=agent,
                arguments=arguments,
            )

            # MCP results already contain a success field.
            # Local results retain the previous success behavior.
            tool = self.tool_execution_service.tool_registry.get_tool(
                action
            )

            if tool["type"] == "mcp":
                execution_result = {
                    "success": result["success"],
                    "action": action,
                    "result": result.get("result"),
                    "source": "mcp",
                }

                if not result["success"]:
                    execution_result["error"] = str(
                        result.get("result", "MCP execution failed")
                    )

            else:
                execution_result = {
                    "success": True,
                    "action": action,
                    "result": result,
                    "source": "local",
                }

        except Exception as e:  # noqa: BLE001
            logger.exception("Tool execution failed: %s", action)

            execution_result = {
                "success": False,
                "action": action,
                "error": str(e),
            }

        self.results.append(execution_result)

        self._record_experience(agent, action, execution_result)

        return execution_result

    def _record_experience(self, agent, action, execution_result):
        """
        Stores the execution outcome in the agent's memory.
        """

        try:
            memory_manager = getattr(
                agent,
                "memory_manager",
                None,
            )

            if memory_manager is None:
                return

            experience = {
                "goal": getattr(agent, "goal", ""),
                "action": action,
                "result": str(
                    execution_result.get(
                        "result",
                        execution_result.get("error", ""),
                    )
                ),
                "success": execution_result["success"],
            }

            if hasattr(agent, "energy"):
                experience["energy"] = agent.energy

            if not execution_result["success"]:
                experience["error"] = execution_result.get(
                    "error",
                    "Unknown error",
                )

            memory_manager.record_experience(experience)

        except Exception:  # noqa: BLE001
            logger.exception(
                "Failed to record execution experience"
            )

    async def execute_plan(self, plan, agent):
        """
        Executes a sequence of local or MCP tool steps.
        """

        self.results = []

        for step in plan:
            result = await self.execute_step(step, agent)

            if not result["success"]:
                break

        return {
            "success": self.evaluate_results(),
            "results": self.results,
        }

    def evaluate_results(self):
        """
        Evaluates the results of the executed plan.
        """

        if not self.results:
            return False

        return all(
            result.get("success", False)
            for result in self.results
        )