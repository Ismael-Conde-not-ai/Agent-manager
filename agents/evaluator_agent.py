import json

from api.api_client import geminiAI  #, geminiEmbed, ollamaAI, ollamaEmbed


class EvaluatorAgent:
    """
    Evaluates the outcome of an agent workflow.
    """
    def __init__(self, name = "EvaluatorAgent"):
        self.name = name

    def evaluate(self, goal, research, plan, execution):
        """
        Evaluate the overall performance of the agents based on the provided goal, research, plan, and execution results.
        """
        prompt = f"""
        You are an objective evaluator agent.
        Evaluate wheter the execution actually achieved the goal.

        Goal:
        {goal}

        Research:
        {research}

        Plan:
        {plan}

        Execution results:
        {execution}
        Rules:
        - Check the execution results, not just the plan.
        - A successful tool call does not automatically mean the goal was achieved.
        - If the goal is only partially achieved, return success=false.
        - Do not claim energy efficiency unless energy measurements support it.
        - If the evidence is insufficient, return success=false.
        - Return ONLY valid JSON in this exact format:

        {{
            "success": true,
            "evaluation": "Explain the evidence for the decision"
        }}
        """
        try:
            result = geminiAI(prompt).strip()

            # Remove markdown code fences if the model adds them.
            if result.startswith("```"):
                result = result.split("\n",1)[1]
                result = result.rsplit("```",1)[0].strip()

            data = json.loads(result)

            if not isinstance(data, dict):
                raise ValueError("Evaluation result is not a JSON object")

            if not isinstance(data.get("success"), bool):
                raise ValueError("'success' must be a boolean")

            if not isinstance(data.get("evaluation"), str):
                raise ValueError("'evaluation' must be a string")

            return {
                "success": data["success"],
                "evaluation": data["evaluation"]
            }
        except (json.JSONDecodeError, ValueError, IndexError) as error:
            return {
                "success": False,
                "evaluation": (
                    "Error could not be parsed reliably. "
                    f"Reason: {error}"
                )
            }