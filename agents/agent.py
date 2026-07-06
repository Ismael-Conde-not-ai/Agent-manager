import json
from tools.registry import ToolRegistry
from tools.work import work
from tools.recharge import recharge
from tools.rest import rest
from core.logger import logger
from knowledge.knowledge_base import KnowledgeBase
from tools.search_knowledge import search_knowledge
from pathlib import Path

class AIagent:
    """
    Represents a simple AI agent with a goal, energy level,
    and functions asociated with his features.
    """
    
    from api.apiClient import geminiAI
    from api.apiClient import ollamaAI
    
    def __init__(self,name,goal,initial_energy,initial_status):
        self.name :str = name
        self.goal :str = goal
        self.energy : int = initial_energy
        self.status :str = initial_status
        self.memory = []
        self.plan = []
        self.use_local_model = False #flag to indicate whether to use local model or not

        self.knowledge =KnowledgeBase()

        self.tool_registry = ToolRegistry()
        self.tool_registry.register("work",work)
        self.tool_registry.register("recharge",recharge)
        self.tool_registry.register("rest",rest)
        self.tool_registry.register("search_knowledge",search_knowledge)

        self.load_memory()
    
    

    def showMemory(self):
        '''
        Print the events in the agent's memory
        '''
        print(f"\n Memory of {self.name}:")
        for event in self.memory:
            print("- ",event)

    
    def recentMemory(self,limit=5):
        '''
        Return only the last 5 memory entries
        '''
        return self.memory[-limit:]
    
    
    def execute_tool (self,toolName):
        '''
        Takes a tool as argument then executes the tool and takes the return in the variable result.
        Saves the result and the executed tool and the enrgy in memory.
        Saves the memory in the memory.json using method save_memory()
        '''
        result = self.tool_registry.execute(toolName,self)
        logger.info(f"{self.name} executed tool: {toolName}")
        logger.info(f"{self.name} energy level: {self.energy}")
        self.memory.append(result)
        self.memory.append({"action": toolName,
                            "result": result,
                            "energy": self.energy})
        self.save_memory()


    def create_plan (self):
        """
        Creates a structured plan for the agent to follow.
        """

        context = self.get_relevant_context()
        memory_context = self.get_memory_context()

        prompt = f"""
        You are an advanced AI agent.

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


    def parse_plan(self,plan_text):
        '''
        Parses the plan text into a list of steps.
        '''
        try:
            plan = json.loads(plan_text)
            return [step["action"] for step in plan]
        except json.JSONDecodeError:
            return ["rest"]  # Default action if parsing fails
        

    def execute_plan_step (self):
        '''
        Executes the plan created with AI, if not plan it returns none.
        calls execute_tool to use the tool and saves a binnacle in memory
        '''
        if not self.plan:
            print("No plan available")
            return
        step = self.plan.pop(0)
        
        decision_text = self.decide_next_action(step)
        logger.info(f"RAW decision output: {decision_text}")

        action,decision_data = self.parse_action(decision_text)

        # Validate action against available tools
        if action not in self.tool_registry.list_tools():
            logger.info(f"{self.name} invalid action, using fallback")
            if self.energy < 30:
                action = "recharge"
            else:
                action = step 
        
        logger.info(f"{self.name} planned step: {step}")
        logger.info(f"{self.name} final action: {action}")

        self.execute_tool(action)
        self.memory.append(f"Plan step executed: {step}")


    def autonomousStep (self):
        '''
        Calls methods to create a plan and then execute it. 
        '''
        if not self.plan:
            self.create_plan()
        self.execute_plan_step()


    def load_memory(self):
        '''
        Loads memory fron memory.json to memory atribute.
        '''
        memory_path = Path(__file__).resolve().parent.parent / "data" / "memory.json"
        try:
            with memory_path.open("r", encoding="utf-8") as file:
                self.memory = json.load(file)
        except Exception as e:
            print("Memory load failed:", e)
            self.memory = []

    
    def save_memory(self):
        '''
        Saves the memory[] atribute to a memory.json.
        '''
        with open("data/memory.json","w") as file:
            json.dump(self.memory,file,indent=2)
            

    def get_relevant_context(self):
        '''
        Searchs information inside knowledge instance atributes using search method
        saves the relevant information in context and return the information in a formatted string
        '''
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
        
        
    def decide_next_action(self,step):
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
            - Choose the BEST action based on context
            - If the step is not optimal, override it
            - If energy is below 30, prioritize recharge or rest
            - Prioritize:
            1. Getting information (search_knowledge) if needed
            2. Energy management (recharge/rest) if low energy
            3. Execution (work) when ready

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
    
    
    def parse_action(self,decision_text):
        """
        Parses the decision text into a structured action and reasoning.
        """
        try:
            desicion = json.loads(decision_text)
            return desicion.get("action"),desicion
        except json.JSONDecodeError:
            return "rest", {"error": "invalid json"}
        
    
    def get_memory_context(self):
        """
        Returns the recent memory context for the agent.
        """
        if not self.memory:
            return "No past experience"
        recent_memory = self.recentMemory()
        
        formatting = []

        for m in recent_memory:
            if isinstance(m,dict):
                formatting.append(
                    f"-action: {m['action']}, result: {m['result']}, energy: {m['energy']}"
                    )
            else:
                formatting.append(m)
        formatted = "\n".join(formatting)

        return f"""
                Recent Experience:
                {formatted}
                """