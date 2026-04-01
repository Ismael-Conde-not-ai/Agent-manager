import json
from tools.registry import ToolRegistry
from tools.work import work
from tools.recharge import recharge
from tools.rest import rest
from core.logger import logger
from knowledge.knowledge_base import KnowledgeBase
from tools.search_knowledge import search_knowledge

class AIagent:
    """
    Represents a simple AI agent with a goal, energy level,
    and functions asociated with his features.
    """
    
    from api.apiClient import geminiAI
    
    def __init__(self,name,goal,initial_energy,initial_status):
        self.name :str = name
        self.goal :str = goal
        self.energy : int = initial_energy
        self.status :str = initial_status
        self.memory = []
        self.plan = []

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
        self.memory.append(f"Executed tool: {toolName} | Energy: {self.energy}")
        self.save_memory()

    def create_plan (self):

        context = self.get_relevant_context()

        prompt =f"""
        You are an autonomous AI agent.

        Agent name: {self.name}
        Goal: {self.goal}

        reelevant knowledge: {context}

        recent memory: {self.memory[:-5]}

        Available tools:
        {", ".join(self.tool_registry.list_tools())}

        Instructions:
        - Think step by step
        - Use the knowledge if relevant
        - Create a short plan using tool names only

        Return 3 to 5 steps using only the tool names.
        """
        gemini =self.geminiAI
        plan_text =gemini(prompt).strip().lower()
        self.plan = plan_text.split("\n")
        logger.info(f"{self.name} generated a new plan: {self.plan}")
        print("\nGenerated Plan:")
        for step in self.plan:
            print("-", step)

        logger.info(f"{self.name} used context: {context[:100]}")
    
    def execute_plan_step (self):
        '''
        Executes the plan created with AI, if not plan it returns none.
        calls execute_tool to use the tool and saves a binnacle in memory
        '''
        if not self.plan:
            print("No plan available")
            return
        step = self.plan.pop(0)
        
        decision = self.decide_next_action(step)

        action = self.parse_action(decision)

        if action not in self.tool_registry.list_tools():
            action = step 
        
        logger.info(f"{self.name} decision: {decision}")
        logger.info(f"{self.name} chose action: {action}")

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
        try:
            with open("data/memory.json","r") as file:
                self.memory = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.memory=[]
    
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

        context = self.get_relevant_context()

        prompt = f"""
        You are an intelligent AI agent.

        Goal:
        {self.goal}

        Current step:
        {step}

        Relevant knowledge:
        {context}

        Recent memory:
        {self.memory[-5:]}

        Available tools:
        {", ".join(self.tool_registry.list_tools())}

        Instructions:
        - Decide the best tool to use
        - Explain your reasoning
        - Be concise

        Return in this format:
        Action: <tool_name>
        Reason: <short explanation>
        
        """
        response = self.geminiAI(prompt)
        output = response.strip().lower()
        return output
    
    def parse_action(self,decision_text):

        lines = decision_text.split("\n")
        action = None

        for line in lines:
            if "action" in line:
                action = line.split("action:")[-1].strip()
        return action