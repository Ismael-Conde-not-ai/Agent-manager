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

    
    def replan(self, goal, previous_plan, execution_results, research=None):
        """
        Create a revised plan based on previous execution results.
        """
        research_context = (
            research if research else "No research available."
        )

        memory_context = self.memory_context_builder.build(goal)

        if not memory_context:
            memory_context = "No relevant past experiences found."

        prompt = f"""
        You are an adaptive planning AI agent.

        Your task is to revise a plan after execution feedback.

        Goal:
        {goal}

        Previous plan:
        {previous_plan}

        Execution results:
        {execution_results}

        Research information:
        {research_context}

        Relevant memory from previous experiences:
        {memory_context}

        Instructions:
        - Analyze which actions succeeded and which failed.
        - Do not assume failed actions succeeded.
        - Avoid repeating a failed action without a justified reason.
        - Apply relevant lessons from previous experiences.
        - Create a revised plan that addresses the remaining goal.
        - Use only these actions:
        search_knowledge, work, recharge, rest.
        - Return between 2 and 5 steps.
        - Do not execute any action.
        - Return ONLY valid JSON.

        Required format:
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

    
    def validate_plan(self, plan):
        """
        Validate the structure and allowed actions of a plan.

        Returns:
            tuple[bool, str | None]: validation status and error message.
        """
        allowed_actions = {
            "search_knowledge",
            "work",
            "recharge",
            "rest",
        }

        if not isinstance(plan, list):
            return False, "Plan must be a list."

        if not 2 <= len(plan) <= 5:
            return False, "Plan must contain between 2 and 5 steps."

        required_fields = {"step", "action", "description"}

        for index, item in enumerate(plan, start=1):
            if not isinstance(item, dict):
                return False, f"Step {index} must be an object."

            if not required_fields.issubset(item.keys()):
                return False, f"Step {index} is missing required fields."

            step_number = item["step"]

            if (
                not isinstance(step_number, int)
                or isinstance(step_number, bool)
                or step_number != index
            ):
                return False, (
                    f"Step number at position {index} must be {index}."
                )

            action = item["action"]

            if not isinstance(action, str) or action not in allowed_actions:
                return False, (
                    f"Step {index} contains an unsupported action."
                )

            description = item["description"]

            if not isinstance(description, str) or not description.strip():
                return False, (
                    f"Step {index} must have a non-empty description."
                )

        return True, None
