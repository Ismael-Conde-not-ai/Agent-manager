from core.contracts import (
    ErrorCategory,
    ErrorInfo,
    EvaluationResult,
    ExecutionResult,
    Plan,
    ResearchResult,
    WorkflowAttempt,
    WorkflowResult,
)
from core.exceptions import (
    AgentError,
    InternalAgentError,
    PlanningError,
    ValidationError,
)
from core.logger import logger


class Orchestrator:

    def __init__(
        self,
        manager=None,
        agents=None,
        *,
        research_agent=None,
        planner_agent=None,
        executor_agent=None,
        evaluator_agent=None,
    ):
        self.manager = manager
        composed_agents = agents or {}
        self.agents = {
            "ResearchAgent": (
                research_agent or composed_agents.get("ResearchAgent")
            ),
            "PlannerAgent": (
                planner_agent or composed_agents.get("PlannerAgent")
            ),
            "ExecutorAgent": (
                executor_agent or composed_agents.get("ExecutorAgent")
            ),
            "EvaluatorAgent": (
                evaluator_agent or composed_agents.get("EvaluatorAgent")
            ),
        }

    async def run(self, goal, agent, max_retries=1):
        agents = self.agents
        if not any(agents.values()) and self.manager is not None:
            agents = {
                name: self.manager.get_agent(name)
                for name in self.agents
            }

        for name, registered_agent in agents.items():
            if registered_agent is None:
                raise ValidationError(
                    f"{name} not found.",
                    code="missing_agent",
                )

        research_agent = agents["ResearchAgent"]
        planner_agent = agents["PlannerAgent"]
        executor_agent = agents["ExecutorAgent"]
        evaluator_agent = agents["EvaluatorAgent"]

        if (
            not isinstance(max_retries, int)
            or isinstance(max_retries, bool)
            or max_retries < 0
        ):
            raise ValidationError(
                "max_retries must be a non-negative integer.",
                code="invalid_retry_limit",
            )

        logger.info("[ORCHESTRATOR] Starting task: %s", goal)

        # These agents remain synchronous for now.
        try:
            research_result = ResearchResult(
                text=str(research_agent.research(goal))
            )
        except AgentError as error:
            return self._failed_workflow(goal, error)
        except Exception as error:
            wrapped = InternalAgentError(
                "Research stage failed.",
                code="research_stage_failed",
                cause=error,
            )
            logger.exception(
                "[ORCHESTRATOR] category=%s code=%s",
                wrapped.category.value,
                wrapped.code,
            )
            return self._failed_workflow(goal, wrapped)

        attempts = []
        previous_plans = []
        previous_plan = None
        previous_feedback = None

        for attempt_number in range(max_retries + 1):
            attempt_id = attempt_number + 1

            logger.info(
                "[ORCHESTRATOR] Attempt %s/%s",
                attempt_id,
                max_retries + 1,
            )

            if previous_plan is not None and previous_feedback is not None:
                logger.info("[ORCHESTRATOR] Revising previous plan")

                try:
                    plan_text = planner_agent.replan(
                        goal=goal,
                        previous_plan=previous_plan,
                        execution_results=previous_feedback,
                        research=research_result,
                    )
                except AgentError as error:
                    return self._failed_workflow(
                        goal,
                        error,
                        research=research_result,
                        attempts=attempts,
                    )
            else:
                logger.info("[ORCHESTRATOR] Creating initial plan")

                try:
                    plan_text = planner_agent.create_plan(
                        goal,
                        research_result,
                    )
                except AgentError as error:
                    return self._failed_workflow(
                        goal,
                        error,
                        research=research_result,
                        attempts=attempts,
                    )

            try:
                plan = Plan.from_legacy(
                    planner_agent.parse_plan(plan_text)
                )
                is_valid, validation_error = (
                    planner_agent.validate_plan(plan)
                )
            except AgentError as error:
                return self._failed_workflow(
                    goal,
                    error,
                    research=research_result,
                    attempts=attempts,
                )
            except Exception as error:
                wrapped = PlanningError(
                    "Plan interpretation failed.",
                    code="plan_interpretation_failed",
                    cause=error,
                )
                logger.exception(
                    "[ORCHESTRATOR] category=%s code=%s",
                    wrapped.category.value,
                    wrapped.code,
                )
                return self._failed_workflow(
                    goal,
                    wrapped,
                    research=research_result,
                    attempts=attempts,
                )

            if not is_valid:
                error_message = (
                    validation_error or "The generated plan is invalid."
                )

                logger.warning(
                    "[ORCHESTRATOR] Invalid plan rejected: %s",
                    error_message,
                )

                attempts.append(
                    WorkflowAttempt(
                        attempt=attempt_id,
                        plan=plan,
                        success=False,
                        error=ErrorInfo(
                            code="invalid_plan",
                            message=error_message,
                            category=ErrorCategory.PLANNING,
                        ),
                    )
                )

                previous_plan = plan
                previous_feedback = {
                    "success": False,
                    "error": "Plan validation failed.",
                    "validation_error": error_message,
                    "instructions": (
                        "Correct the rejected plan. Follow the "
                        "validation error and use only allowed actions."
                    ),
                }

                continue

            if plan in previous_plans:
                logger.warning(
                    "[ORCHESTRATOR] Planner repeated a previous plan."
                )

            previous_plans.append(plan)

            logger.info(
                "[ORCHESTRATOR] Plan validated: %s",
                plan,
            )

            # MCP execution is asynchronous.
            try:
                execution = await executor_agent.execute_plan(
                    plan,
                    agent,
                )
            except AgentError as error:
                execution = ExecutionResult(
                    success=False,
                    error=error.to_error_info(),
                )
            except Exception as error:
                wrapped = InternalAgentError(
                    "Execution stage failed.",
                    code="execution_stage_failed",
                    cause=error,
                )
                logger.exception(
                    "[ORCHESTRATOR] category=%s code=%s",
                    wrapped.category.value,
                    wrapped.code,
                )
                execution = ExecutionResult(
                    success=False,
                    error=wrapped.to_error_info(),
                )
            if not isinstance(execution, ExecutionResult):
                execution = ExecutionResult.from_legacy(
                    execution,
                    plan=plan,
                )

            execution_success = execution.success

            # Evaluator remains synchronous.
            try:
                evaluation = evaluator_agent.evaluate(
                    goal,
                    research_result,
                    plan,
                    execution,
                )
            except AgentError as error:
                evaluation = EvaluationResult(
                    success=False,
                    evaluation="Evaluation could not be completed.",
                    error=error.to_error_info(),
                )
            except Exception as error:
                wrapped = InternalAgentError(
                    "Evaluation stage failed.",
                    code="evaluation_stage_failed",
                    cause=error,
                )
                logger.exception(
                    "[ORCHESTRATOR] category=%s code=%s",
                    wrapped.category.value,
                    wrapped.code,
                )
                evaluation = EvaluationResult(
                    success=False,
                    evaluation="Evaluation could not be completed.",
                    error=wrapped.to_error_info(),
                )
            if not isinstance(evaluation, EvaluationResult):
                evaluation = EvaluationResult.from_legacy(evaluation)

            evaluation_success = evaluation.success
            success = execution_success and evaluation_success

            attempt = WorkflowAttempt(
                attempt=attempt_id,
                plan=plan,
                execution=execution,
                evaluation=evaluation,
                success=success,
            )

            attempts.append(attempt)

            logger.info(
                "[ORCHESTRATOR] Execution success: %s",
                execution_success,
            )
            logger.info(
                "[ORCHESTRATOR] Evaluation success: %s",
                evaluation_success,
            )

            if success:
                logger.info("[ORCHESTRATOR] Goal achieved")
                break

            previous_plan = plan
            previous_feedback = {
                "execution": execution,
                "evaluation": evaluation,
            }

            if attempt_number < max_retries:
                if (
                    execution.error is not None
                    and not execution.error.retryable
                ) or (
                    evaluation.error is not None
                    and not evaluation.error.retryable
                ):
                    break
                logger.warning(
                    "[ORCHESTRATOR] Attempt unsuccessful. "
                    "The next attempt will replan."
                )

        final_attempt = attempts[-1]
        return WorkflowResult(
            success=final_attempt.success,
            goal=goal,
            research=research_result,
            attempts=attempts,
            final_plan=final_attempt.plan,
            final_execution=final_attempt.execution,
            final_evaluation=final_attempt.evaluation,
            error=final_attempt.error,
        )

    @staticmethod
    def _failed_workflow(
        goal,
        error,
        *,
        research=None,
        attempts=None,
    ):
        return WorkflowResult(
            success=False,
            goal=goal,
            research=research,
            attempts=attempts or [],
            error=error.to_error_info(),
        )