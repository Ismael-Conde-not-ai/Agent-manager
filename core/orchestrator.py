
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

        if (
            not isinstance(max_retries, int)
            or isinstance(max_retries, bool)
            or max_retries < 0
        ):
            raise ValueError(
                "max_retries must be a non-negative integer."
            )

        logger.info("[ORCHESTRATOR] Starting task: %s", goal)

        research_result = research_agent.research(goal)

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

            # Create the initial plan or revise a previous one.
            if previous_plan is not None and previous_feedback is not None:
                logger.info("[ORCHESTRATOR] Revising previous plan")

                plan_text = planner_agent.replan(
                    goal=goal,
                    previous_plan=previous_plan,
                    execution_results=previous_feedback,
                    research=research_result,
                )
            else:
                logger.info("[ORCHESTRATOR] Creating initial plan")

                plan_text = planner_agent.create_plan(
                    goal,
                    research_result,
                )

            plan = planner_agent.parse_plan(plan_text)

            # Validate before execution. Invalid plans must never
            # reach ExecutorAgent.
            is_valid, validation_error = planner_agent.validate_plan(
                plan
            )

            
            if not is_valid:
                error_message = (
                    validation_error or "The generated plan is invalid."
                )

                logger.warning(
                    "[ORCHESTRATOR] Invalid plan rejected: %s",
                    error_message,
                )

                attempts.append({
                    "attempt": attempt_id,
                    "plan": plan,
                    "success": False,
                    "error": error_message,
                })

                # Send the validation error to the planner
                # during the next attempt.
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

            # Warn if the planner repeats an earlier plan.
            if plan in previous_plans:
                logger.warning(
                    "[ORCHESTRATOR] Planner repeated a previous plan."
                )

            previous_plans.append(plan.copy())

            logger.info(
                "[ORCHESTRATOR] Plan validated: %s",
                plan,
            )

            execution = executor_agent.execute_plan(plan, agent)
            execution_success = execution.get("success") is True

            evaluation = evaluator_agent.evaluate(
                goal,
                research_result,
                plan,
                execution,
            )
            evaluation_success = evaluation.get("success") is True

            success = execution_success and evaluation_success

            attempt = {
                "attempt": attempt_id,
                "plan": plan,
                "execution": execution,
                "evaluation": evaluation,
                "success": success,
            }

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

            # Preserve execution and evaluation feedback for replanning.
            previous_plan = plan
            previous_feedback = {
                "execution": execution,
                "evaluation": evaluation,
            }

            if attempt_number < max_retries:
                logger.warning(
                    "[ORCHESTRATOR] Attempt unsuccessful. "
                    "The next attempt will replan."
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
                None
                if final_attempt["success"]
                else final_attempt.get(
                    "error",
                    "Goal not achieved after permitted attempts.",
                )
            ),
        }
