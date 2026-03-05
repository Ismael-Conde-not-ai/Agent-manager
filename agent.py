class AIagent:
    """
    Represents a simple AI agent with a goal, energy level,
    and basic actions such as think, act, and recharge.
    """
    from utils import energyCalculator
    from apiClient import geminiAI
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

    def think(self):
        '''
        prints the agent's thoughts and what is willing to do
        '''
        self.status='Thinking'
        self.memory.append("Agent is thinking")
        print(f"the agent {self.name} is thinking")
    
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

    def info(self):
        '''
        Prints agent's informationthin
        '''
        print(f"\n🤖 Agent: {self.name}\n 🎯 Goal: {self.goal}\n 🔋 Energy level: {self.energy}%\n 🏗️ Status: {self.status}")

    def showMemory(self):
        '''
        Print the events in the agent's memory
        '''
        print(f"\n Memory of {self.name}:")
        for event in self.memory:
            print("- ",event)
    
    def thinkAi (self):
        '''
        Send a promt to gemimi 3 flash using name and goal of the agent, uses recent memory 5 entries
        '''
        gemini = self.geminiAI
        prevoiusActions= self.recentMemory()
        
        memory_text="\n".join(prevoiusActions) if prevoiusActions else "No previous actions."
        tools_list = "\n".join(self.tools.keys())
        prompt:str=f"""
        You are an AI agent named {self.name}. 
        Your goal is: {self.goal}.
        your current energy level is: {self.energy}. 
        Previous actions: {memory_text}
        Available tools:
        {tools_list}
        choose the best tool for the situation.
        Respond only with the tool name.
        """
        decision =gemini(prompt).strip().lower()
        self.memory.append(f"AI decision: {decision}")
        print(f"\nAi decision for {self.name}:")
        print(decision)
        return decision
    
    def recentMemory(self,limit=5):
        '''
        Return only the last 5 memory entries
        '''
        return self.memory[-limit:]
    """
    def executeDecision (self, decision):
        if decision == "work":
            self.act()
        elif decision == "recharge":
            self.recharge()
        elif decision == "rest":
            self.memory.append("The agent is resting")
        else:
            self.memory.append(f"Invalid decision: {decision}")
    """
    def execute_tool (self,toolName):
        if toolName in self.tools:
            self.tools[toolName]()
            self.memory.append(f"executed tool: {toolName}")
        else:
            self.memory.append(f"Invalid tool: {toolName}")

    def autonomousStep (self):
        decision_tool =self.thinkAi()
        #self.executeDecision(decision)
        self.execute_tool(decision_tool)