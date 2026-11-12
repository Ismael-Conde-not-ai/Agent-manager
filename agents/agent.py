import asyncio
import json
from pathlib import Path

from api.api_client import geminiAI, ollamaAI
from core.contracts import Plan
from core.logger import logger
from knowledge.knowledge_base import KnowledgeBase
from memory.memory_context_builder import MemoryContextBuilder
from memory.memory_manager import MemoryManager
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

    def __init__(
        self,
        name,
        goal,
        initial_energy,
        initial_status,
        knowledge_base=None,
        memory_manager=None,
        tool_registry=None,
        tool_execution_service=None,
        planner_agent=None,
        executor_agent=None,
        orchestrator=None,
    ):
        self.name: str = name
        self.goal: str = goal
        self.energy: int = initial_energy
        self.status: str = initial_status
        self.short_term_memory = []
        self.long_term_memory = []
        self.plan = None
        self.use_local_model = False # Flag to indicate whether to use local model or not

        self.geminiAI = geminiAI
        self.ollamaAI = ollamaAI

        self.knowledge = (
            knowledge_base
            if knowledge_base is not None
            else KnowledgeBase()
        )
        self.memory_manager = (
            memory_manager
            if memory_manager is not None
            else MemoryManager()
        )
        self.memory_context_builder = MemoryContextBuilder(self.memory_manager)
        self.tool_execution_service = tool_execution_service
        self.planner_agent = planner_agent
        self.executor_agent = executor_agent
        self.orchestrator = orchestrator

        self.tool_registry = (
            tool_registry
            if tool_registry is not None
            else ToolRegistry()
        )
        if tool_registry is None:
            self.tool_registry.register("work", work)
            self.tool_registry.register("recharge", recharge)
            self.tool_registry.register("rest", rest)
            self.tool_registry.register("search_knowledge", search_knowledge)

        self.load_memory()
    
    def execute_tool(self, toolName):
        """
        Executes a tool, records its result, reflects on the action,
        and saves the agent's memory.
        """
        if self.executor_agent is not None:
            result = self._run_coroutine(
                self.executor_agent.execute_step(
                    {
                        "step": 1,
                        "action": toolName,
                        "description": "Legacy tool execution",
                    },
                    self,
                )
            )
            success = result.success
            result_text = result.result if success else result.error.message
        else:
            try:
                result_text = self.tool_registry.execute(toolName, self)
                success = True
            except Exception as e:  # noqa: BLE001
                result_text = f"error: {str(e)}"  # noqa: RUF010
                success = False

        logger.info(f"{self.name} success: {success}")
        logger.info(f"{self.name} executed tool: {toolName}")
        logger.info(f"{self.name} energy level: {self.energy}")

        memory_entry = {
            "action": toolName,
            "result": str(result_text),
            "success": success,
            "energy": self.energy,
        }

        # Update short-term and long-term memory.
        self.short_term_memory.append(memory_entry)
        self.short_term_memory = self.short_term_memory[-5:]

        self.long_term_memory.append(memory_entry)
        self.long_term_memory = self.long_term_memory[-100:]

        # Reflect on the action.
        reflection = ""
        try:
            reflection = self.reflect_on_action(memory_entry)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to reflect on agent action")
            reflection = "Reflection failed."

        self.long_term_memory.append({"reflection": reflection})
        self.short_term_memory.append({"reflection": reflection})

        self.short_term_memory = self.short_term_memory[-5:]
        self.long_term_memory = self.long_term_memory[-100:]

        # Record the experience once, including the lesson.
        experience = {
            "goal": self.goal,
            "action": toolName,
            "result": str(result_text),
            "success": success,
            "energy": self.energy,
            "lesson": reflection,
        }

        if not success:
            experience["error"] = str(result_text)

        try:
            self.memory_manager.record_experience(experience)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to save agent experience")

        self.save_memory()
        return success

    def create_plan(self):
        """
        Creates a structured plan for the agent to follow.
        """
        if self.planner_agent is not None:
            self.plan = self.parse_plan(
                self.planner_agent.create_plan(self.goal)
            )
            return self.plan

        context = self.get_relevant_context()
        memory_context = self.get_extended_memory_context()

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
        self.plan = self.plan[:5] if self.plan else None
        print(f"{self.name} generated structured plan: {self.plan}")
        logger.info(f"{self.name} generated structured plan: {self.plan}")
        logger.info(f"{self.name} used context: {context[:100]}")

    def parse_plan(self, plan_text):
        """
        Parses the plan text into a list of steps.
        """
        if self.planner_agent is not None:
            return self.planner_agent.parse_plan(plan_text)
        try:
            plan = json.loads(plan_text)
            return Plan.from_legacy(plan)
        except (json.JSONDecodeError, TypeError, KeyError):
            logger.warning("%s generated an invalid plan", self.name)
            return []

    def autonomousStep(self):
        """
        Calls methods to create a plan and then executes the plan created with AI, 
        if not plan it returns none, calls execute_tool to use the tool and saves a binnacle in memory.
        """
        if self.orchestrator is None:
            raise RuntimeError(
                "AIagent requires the composed Orchestrator "
                "for autonomous execution."
            )
        return self._run_coroutine(self.autonomous_step())

    async def autonomous_step(self):
        """Run the historical step endpoint through the central workflow."""
        if len(self.long_term_memory) > 100:
            logger.info("%s memory limit reached, stopping agent.", self.name)
            return None

        result = await self.orchestrator.run(
            self.goal,
            self,
            max_retries=0,
        )
        self._sync_workflow_state(result)
        return result

    def _sync_workflow_state(self, workflow_result):
        execution = workflow_result.final_execution
        if execution is None:
            self.plan = workflow_result.final_plan
            return

        executed_steps = len(execution.results)
        final_plan = workflow_result.final_plan
        if final_plan is not None and executed_steps < len(final_plan):
            self.plan = Plan(
                steps=final_plan.steps[executed_steps:]
            )
        else:
            self.plan = None

        for step_result in execution.results:
            entry = {
                "action": step_result.step.action,
                "result": str(step_result.result.result),
                "success": step_result.result.success,
                "energy": self.energy,
            }
            self.short_term_memory.append(entry)
            self.long_term_memory.append(entry)
        self.short_term_memory = self.short_term_memory[-5:]
        self.long_term_memory = self.long_term_memory[-100:]
        self.save_memory()

    @staticmethod
    def _run_coroutine(coroutine):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coroutine)
        coroutine.close()
        raise RuntimeError(
            "Synchronous AIagent compatibility methods cannot run "
            "inside an active event loop; use autonomous_step()."
        )

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
        Retrieves relevant knowledge and formats it as readable context.
        """
        try:
            context = self.knowledge.get_context(
                query=self.goal, 
                limit=3, 
                max_characters=2000
            )
            if not context or context == "No relevant knowledge found.":
                return "No relevant knowledge found."

            return f"Relevant Knowledge:\n{context}"

        except Exception:  # noqa: BLE001
            logger.exception("Failed to retrieve relevant knowledge")
            return "No relevant knowledge found."

    def decide_next_action(self, step):
        """
        Decides the next action for the agent based on the current step.
        """
        context = self.get_relevant_context()
        memory_context = self.get_extended_memory_context()

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

    def get_extended_memory_context(self):
        """
        Combines recent memory with relevant stored experiences
        """
        recent_context = self.get_memory_context()
        stored_context = self.memory_context_builder.build(self.goal)

        return "\n".join(
            part for part in [recent_context, stored_context] if part
        )