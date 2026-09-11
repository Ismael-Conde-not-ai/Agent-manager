import json

from api.api_client import geminiAI #, geminiEmbed, ollamaAI, ollamaEmbed


class PlannerAgent:
    """
    A class to represent a planner agent.
    """
    def __init__(self, name="PlannerAgent"):
        self.name = name

    def create_plan(self, goal, research=None):
        """
        Create a plan based on the given goal and optional research.
        """
        research_context = research if research else "No research available."

        prompt = f"""
        You are a planning AI agent.

        Your job is to transform a goal into a structured sequence of actions.

        Goal:
        {goal}

        Research information:
        {research_context}

        Instructions:

        - Break the goal into logical steps.
        - Use simple and realistic actions.
        - Consider the available information.
        - Do not execute any action.
        - Only create the plan.
        - Return ONLY valid JSON.
        - The plan must contain between 2 and 5 steps.

        Available actions:

        - search_knowledge
        - work
        - recharge
        - rest

        Return this structure:

        [
            {{
                "step": 1,
                "action": "action_name",
                "description": "What this step should accomplish"
            }}
        ]
        """
        response = geminiAI(prompt).strip()
        return response

    def parse_plan(self, plan_text):
        """
        Parse the plan text into a structured format.
        """
        try:
            plan = json.loads(plan_text)
            if not isinstance(plan, list):
                return []
            return plan
        except json.JSONDecodeError as e:
            print("Plan parsing failed:", e)
            return []