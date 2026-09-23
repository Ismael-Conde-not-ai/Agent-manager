from core.logger import logger


class Orchestrator:
    def __init__(self, manager):
        self.manager = manager

    def run(self, goal, agent, max_retries=1):
        research_agent = self.manager.get_agent("ResearchAgent")
        planner_agent = self.manager.get_agent("PlannerAgent")
        executor_agent = self.manager.get_agent("ExecutorAgent")
        evaluator_agent = self.manager.get_agent("EvaluatorAgent")

        if not research_agent:
            raise ValueError("ResearchAgent not found.")

        if not planner_agent:
            raise ValueError("PlannerAgent not found.")

        if not executor_agent:
            raise ValueError("ExecutorAgent not found.")

        if not evaluator_agent:
            raise ValueError("EvaluatorAgent not found.")

        logger.info(f"[ORCHESTRATOR] Starting task: {goal}")

        # Research Phase
        research_result = research_agent.research(goal)
        logger.info("[ORCHESTRATOR] Research completed")

        # Planning Phase
        plan_text = planner_agent.create_plan(goal, research_result)
        plan = planner_agent.parse_plan(plan_text)
        if not plan:
            return {
                "success":False,
                "goal":goal,
                "error":"Failed to create a valid plan."
            }
        logger.info(f"[ORCHESTRATOR] Plan created: {plan}")

        # Execution Phase
        execution = executor_agent.execute_plan(plan,agent)
        logger.info(
            f"[ORCHESTRATOR] Execution success:"
            f"{execution['success']}"
        )
        if not execution["success"]:
            if max_retries <= 0:
                return {
                    "success":False,
                    "goal":goal,
                    "plan":plan,
                    "execution":execution,
                    "error":"Execution failed"
                }
            logger.info("[ORCHESTRATOR] Execution failed. Creating a new plan")
            retry_plan_text = planner_agent.create_plan(goal, research_result)
            plan = planner_agent.parse_plan(retry_plan_text)
            execution = executor_agent.execute_plan(plan,agent)

        # Evaluation Phase
        evaluation = evaluator_agent.evaluate(goal, research_result, plan, execution)
        logger.info(
            f"[ORCHESTRATOR] Evaluation:"
            f"{evaluation['evaluation']}"
        )
        if evaluation['success']:
            logger.info("[ORCHESTRATOR] Goal achieved")
            return {
                "success":True,
                "goal":goal,
                "research":research_result,
                "plan":plan,
                "execution":execution,
                "evaluation":evaluation
            }
        if max_retries <= 0:
            return {
                "success":False,
                "goal":goal,
                "research":research_result,
                "plan":plan,
                "execution":execution,
                "evaluation":evaluation,
                "error":"Goal not achieved"
            }
        logger.info("[ORCHESTRATOR] Goal not achieved. Creating a new plan")

        retry_plan_text = planner_agent.create_plan(goal, research_result)
        retry_plan = planner_agent.parse_plan(retry_plan_text)
        retry_execution = executor_agent.execute_plan(retry_plan,agent)
        retry_evaluation = evaluator_agent.evaluate(goal, research_result, retry_plan, retry_execution)
        return {
            "success":retry_evaluation['success'],
            "goal":goal,
            "research":research_result,
            "plan":plan,
            "execution":execution,
            "evaluation":evaluation,
            "retry_plan":retry_plan,
            "retry_execution":retry_execution,
            "retry_evaluation":retry_evaluation
        }