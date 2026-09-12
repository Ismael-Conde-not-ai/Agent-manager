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

    def research_plan_and_execute(self, goal, agent):
        """
        Conducts research, creates a plan, and executes it.
        """
        research_agent = self.get_agent("ResearchAgent")
        planner_agent = self.get_agent("PlannerAgent")
        executor_agent = self.get_agent("ExecutorAgent")

        if not research_agent:
            raise ValueError("ResearchAgent not found.")
        if not planner_agent:
            raise ValueError("PlannerAgent not found.")
        if not executor_agent:
            raise ValueError("ExecutorAgent not found")

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
                "error": "No valid plan generated"
            }
        logger.info(f"[WORKFLOW] Plan generated: {plan}")

        #Execution phase
        execution_results = executor_agent.execute_plan(plan, agent)
        logger.info("[WORKFLOW] Plan execution completed")

        return {
            "goal": goal,
            "research": research_result,
            "plan": plan,
            "execution": execution_results
        }
