from core.contracts import (
    ErrorCategory,
    ErrorInfo,
    ExecutionResult,
    Plan,
    PlanStep,
    StepExecutionResult,
    ToolResult,
)
from core.logger import logger
from core.exceptions import AgentError, ToolExecutionError


class ExecutorAgent:

    def __init__(
        self,
        tool_execution_service,
        name="ExecutorAgent",
    ):
        self.name = name
        self.tool_execution_service = tool_execution_service
        self.results = []

    async def execute_step(self, step, agent):
        """
        Executes one local or MCP tool and records its outcome.
        """

        if isinstance(step, PlanStep):
            step_model = step
        else:
            step_data = dict(step)
            step_data.setdefault("step", 1)
            step_data.setdefault("description", "Execute tool step")
            step_model = PlanStep(**step_data)
        action = step_model.action
        arguments = step_model.arguments

        if not action:
            return ToolResult(
                success=False,
                action="unknown",
                source="local",
                error=ErrorInfo(
                    code="missing_action",
                    message="Missing tool action",
                    category=ErrorCategory.VALIDATION,
                ),
            )

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
                execution_result = ToolResult(
                    success=result["success"],
                    action=action,
                    result=result.get("result"),
                    source="mcp",
                    error=(
                        ErrorInfo.model_validate(result["error"])
                        if result.get("error")
                        else ErrorInfo(
                            code="mcp_tool_error",
                            message="MCP tool execution failed.",
                            category=ErrorCategory.TOOL,
                        )
                    )
                    if not result["success"]
                    else None,
                )

            else:
                execution_result = ToolResult(
                    success=True,
                    action=action,
                    result=result,
                    source="local",
                )

        except AgentError as error:
            logger.exception(
                "[EXECUTOR] category=%s code=%s action=%s",
                error.category.value,
                error.code,
                action,
            )

            execution_result = ToolResult(
                success=False,
                action=action,
                source="local",
                error=error.to_error_info(),
            )
        except Exception as error:  # noqa: BLE001
            wrapped = ToolExecutionError(
                f"Tool '{action}' failed.",
                code="unexpected_tool_failure",
                details={"tool_name": action},
                cause=error,
            )
            logger.exception(
                "[EXECUTOR] category=%s code=%s action=%s",
                wrapped.category.value,
                wrapped.code,
                action,
            )

            execution_result = ToolResult(
                success=False,
                action=action,
                source="local",
                error=wrapped.to_error_info(),
            )

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
                error = execution_result.get("error")
                experience["error"] = (
                    error.get("message", "Unknown error")
                    if isinstance(error, dict)
                    else str(error or "Unknown error")
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

        plan_model = plan if isinstance(plan, Plan) else Plan.from_legacy(plan)
        if plan_model is None:
            return ExecutionResult(
                success=False,
                error=ErrorInfo(
                    code="invalid_plan",
                    message="Plan is invalid and cannot be executed.",
                    category=ErrorCategory.VALIDATION,
                ),
            )

        for step in plan_model:
            result = await self.execute_step(step, agent)
            self.results.append(
                StepExecutionResult(step=step, result=result)
            )

            if not result.success:
                break

        return ExecutionResult(
            success=self.evaluate_results(),
            results=self.results,
            error=(
                next(
                    (
                        item.result.error
                        for item in self.results
                        if not item.result.success
                    ),
                    None,
                )
            ),
        )

    def evaluate_results(self):
        """
        Evaluates the results of the executed plan.
        """

        if not self.results:
            return False

        return all(
            (
                result.result.success
                if isinstance(result, StepExecutionResult)
                else result.get("success", False)
            )
            for result in self.results
        )