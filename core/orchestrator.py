from core.logger import logger


class Orchestrator:
    def __init__(self, manager):
        self.manager = manager

    def run(self, goal, agent, max_retries=1):
        research_agent = self.manager.get_agent("ResearchAgent")
        planner_agent = self.manager.get_agent("PlannerAgent")
        executor_agent = self.manager.get_agent("ExecutorAgent")
        evaluator_agent = self.manager.get_agent("EvaluatorAgent")

        agents = {
            "ResearchAgent": research_agent,
            "PlannerAgent": planner_agent,
            "ExecutorAgent": executor_agent,
            "EvaluatorAgent": evaluator_agent,
        }

        for name, registered_agent in agents.items():
            if registered_agent is None:
                raise ValueError(f"{name} not found.")

        if not isinstance(max_retries, int) or isinstance(max_retries, bool):
            raise ValueError("max_retries must be a non-negative integer.")  # noqa: TRY004

        if max_retries < 0:
            raise ValueError("max_retries must be a non-negative integer.")

        logger.info(f"[ORCHESTRATOR] Starting task: {goal}")

        research_result = research_agent.research(goal)
        logger.info("[ORCHESTRATOR] Research completed")

        attempts = []
        previous_plans = []

        # One initial attempt plus the permitted retries.
        for attempt_number in range(max_retries + 1):
            logger.info(
                f"[ORCHESTRATOR] Attempt "
                f"{attempt_number + 1}/{max_retries + 1}"
            )

            plan_text = planner_agent.create_plan(
                goal,
                research_result
            )
            plan = planner_agent.parse_plan(plan_text)

            if not plan:
                attempt = {
                    "attempt": attempt_number + 1,
                    "success": False,
                    "error": "Failed to create a valid plan.",
                }
                attempts.append(attempt)

                if attempt_number < max_retries:
                    logger.warning(
                        "[ORCHESTRATOR] Invalid plan. Retrying."
                    )
                    continue

                break

            # Detect identical consecutive plans.
            if plan in previous_plans:
                logger.warning(
                    "[ORCHESTRATOR] Planner repeated a previous plan."
                )

            previous_plans.append(plan.copy())

            logger.info(f"[ORCHESTRATOR] Plan created: {plan}")

            execution = executor_agent.execute_plan(plan, agent)
            execution_success = execution.get("success") is True

            evaluation = evaluator_agent.evaluate(
                goal,
                research_result,
                plan,
                execution
            )

            evaluation_success = (
                evaluation.get("success") is True
            )

            # The workflow succeeds only if both execution and
            # evaluation report success.
            success = execution_success and evaluation_success

            attempt = {
                "attempt": attempt_number + 1,
                "plan": plan,
                "execution": execution,
                "evaluation": evaluation,
                "success": success,
            }
            attempts.append(attempt)

            logger.info(
                f"[ORCHESTRATOR] Execution success: "
                f"{execution_success}"
            )
            logger.info(
                f"[ORCHESTRATOR] Evaluation success: "
                f"{evaluation_success}"
            )

            if success:
                logger.info("[ORCHESTRATOR] Goal achieved")
                break

            if attempt_number < max_retries:
                logger.warning(
                    "[ORCHESTRATOR] Attempt unsuccessful. Retrying."
                )

        final_attempt = attempts[-1]

        return {
            "success": final_attempt["success"],
            "goal": goal,
            "research": research_result,
            "attempts": attempts,
            "total_attempts": len(attempts),
            "plan": final_attempt.get("plan"),
            "execution": final_attempt.get("execution"),
            "evaluation": final_attempt.get("evaluation"),
            "error": (
                None if final_attempt["success"]
                else final_attempt.get(
                    "error",
                    "Goal not achieved after permitted attempts."
                )
            ),
        }
