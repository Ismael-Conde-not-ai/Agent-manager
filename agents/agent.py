import json
class AIagent:
    """
    Represents a simple AI agent with a goal, energy level,
    and basic actions such as think, act, and recharge.
    """
    from utils.utils import energyCalculator
    from api.apiClient import geminiAI
    def __init__(self,name,goal):
        self.name :str = name
        self.goal :str = goal
        self.energy : int = 100
        self.status :str = 'Idle'
        self.memory = []
        self.tools = {
            "work":self.act,
            "recharge":self.recharge,
            "rest":self.rest
        }
        self.plan = []

        self.load_memory()
    
    def act(self):
        '''
        Spend energy to perform an action
        '''
        if self.energy >= 10:
            calcEnergy = self.energyCalculator
            energy = self.energy
            self.energy = calcEnergy('act',energy)
            self.status ='Working'
            self.memory.append("Agent is working")
            print(f"The agent {self.name} is performing: {self.goal}")
        else:
            self.status ='Out of energy'
            self.memory.append("Agent out of energy")

    def recharge(self):
        '''
        Recharges energy
        '''
        calcEnergy = self.energyCalculator
        energy = self.energy
        self.energy=calcEnergy("recharge",energy)
        self.status = 'Recharged'
        self.memory.append("Agent recharged")
        print(f"Agent {self.name} is recharged")

    def rest(self):
        '''
        The agent rests
        '''
        self.status = "Resting"
        self.memory.append("The agent is resting")

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
        if toolName in self.tools:
            self.tools[toolName]()
            print(f"Tool executed: {toolName}")
            self.memory.append(f"executed tool: {toolName}| Energy: {self.energy}")
            self.save_memory()
        else:
            self.memory.append(f"Invalid tool: {toolName}")

    def create_plan (self):
        prompt =f"""
        You are an autonomous AI agent.

        Agent name: {self.name}
        Goal: {self.goal}

        Available tools:
        {", ".join(self.tools.keys())}

        Create a short plan to achieve the goal.

        Return 3 to 5 steps using only the tool names.
        Example:

        work
        work
        recharge
        rest
        """
        gemini =self.geminiAI
        plan_text =gemini(prompt).strip().lower()
        self.plan = plan_text.split("\n")
        print("\nGenerated Plan:")
        for step in self.plan:
            print("-", step)
    
    def execute_plan_step (self):
        if not self.plan:
            print("No plan available")
            return
        step = self.plan.pop(0)
        print (f"\nExecuting step: {step}")
        self.execute_tool(step)
        self.memory.append(f"Plan step executed: {step}")

    def autonomousStep (self):
        if not self.plan:
            self.create_plan()
        self.execute_plan_step()

    def load_memory(self):

        try:
            with open("data/memory.json","r") as file:
                self.memory = json.load(file)
        except:
            self.memory=[]
    
    def save_memory(self):
        with open("data/memory.json","w") as file:
            json.dump(self.memory,file,indent=2)