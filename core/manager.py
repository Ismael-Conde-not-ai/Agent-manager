from core.logger import logger


class Manager:
    from agents.agent import AIagent
    #from core.logger import logger
    
    def __init__(self):
        self.agents={}
    
    def add_agent(self, agent):
        '''
        adds agent created in ...
        '''
        self.agents[agent.name] = agent

    def get_agent(self, name):
        '''
        returns agent object by name
        '''
        return self.agents.get(name)

    def list_agents(self):
        '''
        returns list of agent names
        '''
        return list(self.agents.keys())

    def research_and_plan(self, goal):
        '''
        takes a goal and orchestrates the research and planning process.
        '''
        research_agent = self.get_agent("ResearchAgent")
        planner_agent = self.get_agent("PlannerAgent")

        if not research_agent:
            raise ValueError("ResearchAgent not found.")
        if not planner_agent:
            raise ValueError("PlannerAgent not found.")

        # Research phase
        logger.info(f"[WORKFLOW] Starting research for: {goal}")
        research_result = research_agent.research(goal)
        logger.info("[WORKFLOW] Research completed")
        # Planning phase
        plan_text = planner_agent.create_plan(goal, research_result)
        logger.info("[WORKFLOW] Planner received plan")

        plan = planner_agent.parse_plan(plan_text)
        if not plan:
            logger.info()("[WORKFLOW] Planner returned an empty plan")

            return {
                "goal": goal,
                "research": research_result,
                "plan": [],
                "error": "Planner returned an empty plan"
            }
        logger.info(f"[WORKFLOW] Plan generated: {plan}")

        return {
            "goal": goal,
            "research": research_result,
            "plan": plan
        }

    def research_plan_and_execute(self, goal, agent, max_retries=1):
        """
        Conducts research, creates a plan, and executes it.
        """
        research_agent = self.get_agent("ResearchAgent")
        planner_agent = self.get_agent("PlannerAgent")
        executor_agent = self.get_agent("ExecutorAgent")
        evaluator_agent = self.get_agent("EvaluatorAgent")

        if not research_agent:
            raise ValueError("ResearchAgent not found.")
        if not planner_agent:
            raise ValueError("PlannerAgent not found.")
        if not executor_agent:
            raise ValueError("ExecutorAgent not found")
        if not evaluator_agent:
            raise ValueError("EvaluatorAgent not found")

        # Research phase
        logger.info(f"[WORKFLOW] Starting research for: {goal}")
        research_result = research_agent.research(goal)
        logger.info("[WORKFLOW] Research completed")

        # Planning phase
        plan_text = planner_agent.create_plan(goal, research_result)
        logger.info("[WORKFLOW] Planner received plan")

        plan = planner_agent.parse_plan(plan_text)
        if not plan:
            logger.info("[WORKFLOW] Planner returned an empty plan")

            return {
                "goal": goal,
                "research": research_result,
                "plan": [],
                "execution": {},
                "error": "No valid plan generated"
            }
        logger.info(f"[WORKFLOW] Plan generated: {plan}")

        #Execution phase
        execution_results = executor_agent.execute_plan(plan, agent)
        evaluation = evaluator_agent.evaluate(goal, research_result, plan, execution_results)
        execution_success = execution_results["success"]
        logger.info("[WORKFLOW] Plan execution completed")
        logger.info(f"[WORKFLOW] Execution success: {execution_success}")
        logger.info(f"[WORKFLOW] Evaluation result: {evaluation['evaluation']}")

        #Execution failure handling and replanning
        if not execution_success and max_retries > 0:
            logger.info("[WORKFLOW] Execution failed. Replanning...")

            retry_plan_text = planner_agent.create_plan(goal, research_result)
            retry_plan = planner_agent.parse_plan(retry_plan_text)
            if not retry_plan:
                return {
                    "goal": goal,
                    "research": research_result,
                    "plan": plan,
                    "execution": execution_results,
                    "retry_plan": [],
                    "error": "Replanning failed."
                }
            logger.info(f"[WORKFLOW] Retry plan generated: {retry_plan}")
            retry_execution = executor_agent.execute_plan(retry_plan, agent)
            #Result of retry execution
            logger.info("[WORKFLOW] Retry execution completed")
            return{
                "goal": goal,
                "research": research_result,
                "plan": plan,
                "execution": execution_results,
                "retry_plan": retry_plan,
                "retry_execution": retry_execution
            }

        if not evaluation["success"]:
            logger.info("[WORKFLOW] Goal not achieved. Replanning...")
            retry_plan_text = planner_agent.create_plan(goal, research_result)
            retry_plan = planner_agent.parse_plan(retry_plan_text)
            retry_execution = executor_agent.execute_plan(retry_plan, agent)
            logger.info("[WORKFLOW] Retry execution completed")
            retry_evaluation = evaluator_agent.evaluate(goal, research_result, retry_plan, retry_execution)
            logger.info(f"[WORKFLOW] Retry evaluation result: {retry_evaluation['evaluation']}")
            return {
                "goal": goal,
                "research": research_result,
                "plan": plan,
                "execution": execution_results,
                "evaluation": evaluation,
                "retry_plan": retry_plan,
                "retry_execution": retry_execution,
                "retry_evaluation": retry_evaluation
            }
        
        # Return the results of the main execution
        return {
            "goal": goal,
            "research": research_result,
            "plan": plan,
            "execution": execution_results,
            "evaluation": evaluation
        }
