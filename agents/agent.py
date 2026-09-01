import json
from pathlib import Path

from api.api_client import geminiAI, ollamaAI
from core.logger import logger
from knowledge.knowledge_base import KnowledgeBase
from tools.recharge import recharge
from tools.registry import ToolRegistry
from tools.rest import rest
from tools.search_knowledge import search_knowledge
from tools.work import work


class AIagent:
    """
    Represents a simple AI agent with a goal, energy level,
    and functions associated with his features.
    """

    def __init__(self, name, goal, initial_energy, initial_status):
        self.name: str = name
        self.goal: str = goal
        self.energy: int = initial_energy
        self.status: str = initial_status
        self.memory = []
        self.short_term_memory = []
        self.long_term_memory = []
        self.plan = []
        self.use_local_model = False # Flag to indicate whether to use local model or not

        self.geminiAI = geminiAI
        self.ollamaAI = ollamaAI

        self.knowledge = KnowledgeBase()

        self.tool_registry = ToolRegistry()
        self.tool_registry.register("work", work)
        self.tool_registry.register("recharge", recharge)
        self.tool_registry.register("rest", rest)
        self.tool_registry.register("search_knowledge", search_knowledge)

        self.load_memory()

    def execute_tool(self, toolName):
        """
        Takes a tool as argument then executes the tool and takes the return in the variable result.
        Saves the result and the executed tool and the energy in memory.
        Saves the memory in the memory.json using method save_memory()
        """
        try:
            result = self.tool_registry.execute(toolName, self)
            success = True
        except Exception as e: #noqa: BLE001
            result = f"error: {str(e)}"  # noqa: RUF010
            success = False

            #logger.error(f"Error executing tool {toolName}: {e}")
        logger.info(f"{self.name} success: {success}")
        logger.info(f"{self.name} executed tool: {toolName}")
        logger.info(f"{self.name} energy level: {self.energy}")

        memory_entry = {
            "action": toolName,
            "result": result,
            "success": success,
            "energy": self.energy
        }
        # Short term memory for reasoning
        self.short_term_memory.append(memory_entry)
        # Limit short term memory to last 5 entries
        self.short_term_memory = self.short_term_memory[-5:]
        # Long term memory for future reference
        self.long_term_memory.append(memory_entry)

        # Reflection on the last action and update memory accordingly
        reflection = self.reflect_on_action(memory_entry)
        self.long_term_memory.append({"reflection": reflection})
        self.short_term_memory.append({"reflection": reflection})
        self.short_term_memory = self.short_term_memory[-5:]   

        self.save_memory()
        return success

    def create_plan(self):
        """
        Creates a structured plan for the agent to follow.
        """

        context = self.get_relevant_context()
        memory_context = self.get_memory_context()

        prompt = f"""
        You are an advanced AI agent.
        Use recent experience to guide your decision.

        Your goal:
        {self.goal}

        {context}

        {memory_context}

        Available tools:
        {", ".join(self.tool_registry.list_tools())}

        Break the goal into a step-by-step plan.

        Return ONLY valid JSON in this format:

        [
        {{"step": 1, "action": "tool_name"}},
        {{"step": 2, "action": "tool_name"}},
        {{"step": 3, "action": "tool_name"}}
        ]

        Rules:
        - Use only available tools
        - 3 to 5 steps
        - Logical order
        
        """
        if getattr(self, 'use_local_model', False):
            ai_function = self.ollamaAI
        else:
            ai_function = self.geminiAI

        plan_text = ai_function(prompt).strip().lower()
        self.plan = self.parse_plan(plan_text)
        print(f"{self.name} generated structured plan: {self.plan}")
        logger.info(f"{self.name} generated structured plan: {self.plan}")

        logger.info(f"{self.name} used context: {context[:100]}")

    def parse_plan(self, plan_text):
        """
        Parses the plan text into a list of steps.
        """
        try:
            plan = json.loads(plan_text)
            return [step["action"] for step in plan]
        except json.JSONDecodeError:
            return ["rest"]  # Default action if parsing fails

    def execute_plan_step(self):
        """
        Executes the plan created with AI, if not plan it returns none.
        calls execute_tool to use the tool and saves a binnacle in memory
        """
        if not self.plan:
            print("No plan available")
            return
        step = self.plan.pop(0)

        decision_text = self.decide_next_action(step)
        logger.info(f"RAW decision output: {decision_text}")

        action, _decision_data = self.parse_action(decision_text)

        # Validate action against available tools
        if action not in self.tool_registry.list_tools():
            logger.info(f"{self.name} invalid action, using fallback")
            if self.energy < 30:
                action = "recharge"
            else:
                action = step

        logger.info(f"{self.name} planned step: {step}")
        logger.info(f"{self.name} final action: {action}")

        success = self.execute_tool(action)
        if not success:
            logger.info(f"{self.name} detected failure, re-planning...")
            #generate a new plan based on memory
            self.plan = []
            self.create_plan()

        #self.short_term_memory.append(f"Plan step executed: {step}")

    def autonomousStep(self):
        """
        Calls methods to create a plan and then execute it.
        """
        if not self.plan:
            self.create_plan()
        self.execute_plan_step()

    def load_memory(self):
        """
        Loads long term memory from memory.json to memory attribute.
        """
        memory_path = Path(__file__).resolve().parent.parent / "data" / "memory.json"
        try:
            with memory_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
                self.long_term_memory = data.get("long_term", [])
        except Exception as e:  # noqa: BLE001
            print("Memory load failed:", e)
            self.long_term_memory = []

    def save_memory(self):
        """
        Saves the long term memory[] attribute to a memory.json.
        Only long term memory is saved, short term memory is not saved.
        """
        with open("data/memory.json","w") as file:
            json.dump({
                "long_term": self.long_term_memory,
            },file,indent=2)

    def get_relevant_context(self):
        """
        Searches information inside knowledge instance attributes using search method
        saves the relevant information in context and return the information in a formatted string
        """
        try:
            context = self.knowledge.search(self.goal)
            formatted = f"""
            Relevant Knowledge:
            -------------------
            {context}
            """
            return formatted
        except TypeError:
            return "No relevant knowledge found"

    def decide_next_action(self, step):
        """
        Decides the next action for the agent based on the current step.
        """
        context = self.get_relevant_context()
        memory_context = self.get_memory_context()

        prompt = f"""
            You are an advanced AI agent.

            Your goal:
            {self.goal}

            Current planned step:
            {step}

            {context}

            {memory_context}

            Available tools:
            {", ".join(self.tool_registry.list_tools())}

            Instructions:
            - You are NOT forced to follow the planned step
            - Use recent experience and reflections to guide your decision.
            - Choose the BEST action based on context
            - If the step is not optimal, override it
            - If energy is below 30, prioritize recharge or rest
            - Prioritize:
            1. Getting information (search_knowledge) if needed
            2. Energy management (recharge/rest) if low energy
            3. Execution (work) when ready
            - If the previous action failed:
                -avoid repeating the same action
                -choose an alternative strategy

            Return ONLY valid JSON:

            {{
            "thought": "...",
            "action": "tool_name",
            "reason": "..."
            }}
            """
        if getattr(self, 'use_local_model', False):
            ai_function = self.ollamaAI
        else:
            ai_function = self.geminiAI

        response = ai_function(prompt)
        output = response.strip().lower()
        return output

    def parse_action(self, decision_text):
        """
        Parses the decision text into a structured action and reasoning.
        """
        try:
            desicion = json.loads(decision_text)
            return desicion.get("action"), desicion
        except json.JSONDecodeError:
            return "rest", {"error": "invalid json"}

    def get_memory_context(self):
        """
        Returns the recent memory context for the agent.
        """
        if not self.short_term_memory:
            return "No recent experience"

        formatted = []

        for m in self.short_term_memory:

            if "action" in m:
                formatted.append(
                    f"- Action: {m['action']}, Result: {m['result']}, Energy: {m['energy']}"
                )

            if "reflection" in m:
                formatted.append(f"- Reflection: {m['reflection']}")

        return f"""
                Recent Experience:
                -------------------
                {chr(10).join(formatted)}
                """

    def get_long_term_summary(self):
        """
        Returns a summary of the long term memory for the agent.
        """
        if not self.long_term_memory:
            return "No long term memory yet."

        return f"Total past actions: {len(self.long_term_memory)}"

    def reflect_on_action(self, last_memory):
        """
        Reflects on the last action taken by the agent and updates memory accordingly.
        """
        context = self.get_relevant_context()

        prompt = f"""
        You are an intelligent AI agent.

        Your goal:
        {self.goal}

        Last action:
        {last_memory}

        Relevant knowledge:
        {context}

        Instructions:
        - Analyze if the action was effective
        - Suggest improvement if needed
        - Be concise

        Return in this format:
        Reflection: <what happened>
        Improvement: <what to do next time>
        """
        response = self.geminiAI(prompt)
        return response.strip()

