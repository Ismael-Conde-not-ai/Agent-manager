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
        prompt:str=f"""
        You are an AI agent named {self.name}. 
        Your goal is: {self.goal}. 
        Previous actions: {memory_text}
        Based in this context, what should you do next? respond bryefly.
        """
        decision =gemini(prompt)
        self.memory.append("AI decision: ",decision)
        print(f"\nAi decision for {self.name}:")
        print(decision)
    
    def recentMemory(self,limit=5):
        '''
        Return only the last 5 memory entries
        '''
        return self.memory[-limit:]