import json

from api.api_client import geminiAI  #, geminiEmbed, ollamaAI, ollamaEmbed
from memory.memory_context_builder import MemoryContextBuilder
from memory.memory_manager import MemoryManager


class PlannerAgent:
    """
    Creates plans using the goal, research, and relevant past experiences.
    """
    def __init__(self, name="PlannerAgent", memory_manager=None):
        self.name = name
        self.memory_manager = (memory_manager if memory_manager is not None else MemoryManager())
        self.memory_context_builder = MemoryContextBuilder(self.memory_manager)

    def create_plan(self, goal, research=None):
        """
        Create a plan based on the given goal and optional research.
        """
        research_context = research if research else "No research available."

        memory_context = self.memory_context_builder.build(goal)

        if not memory_context:
            memory_context = "No relevant past experiences found."

        prompt = f"""
        You are a planning AI agent.

        Your job is to transform a goal into a structured sequence of actions.

        Goal:
        {goal}

        Research information:
        {research_context}

        Relevant memory from previous experiences:
        {memory_context}

        Instructions:

        - Break the goal into logical steps.
        - Use simple and realistic actions.
        - Consider the available information and relevant past experiences.
        - If previous experiences contain useful lessons, apply them.
        - Do not blindly repeat plans that previously failed.
        - Do not assume a previous action succeeded unless memory confirms it.
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