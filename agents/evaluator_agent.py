from api.api_client import geminiAI  #, geminiEmbed, ollamaAI, ollamaEmbed


class EvaluatorAgent:
    """
    A class to represent an evaluator agent.
    """
    def __init__(self, name = "EvaluatorAgent"):
        self.name = name

    def evaluate(self, goal, research, plan, execution):
        """
        Evaluate the overall performance of the agents based on the provided goal, research, plan, and execution results.
        """
        prompt = f"""
        You are an evaluation agent.

        Goal:
        {goal}

        Research:
        {research}

        Plan:
        {plan}

        Execution results:
        {execution}
        """

        result = geminiAI(prompt).strip()

        if "SUCCESS" in result:
            return {
                "success": True,
                "evaluation": result
            }

        return {
            "success": False,
            "evaluation": result
        }