class AIagent:
    """
    Represents a simple AI agent with a goal, energy level,
    and basic actions such as think, act, and recharge.
    """
    from utils import energyCalculator
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
        calcEnergy = self.energyCalculator
        energy = self.energy
        self.energy = calcEnergy('act',energy)
        self.status ='Working'
        self.memory.append("Agent is working")
        print(f"The agent {self.name} is performing: {self.goal}")

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
        print(f"\n Memory of {self.name}:")
        for event in self.memory:
            print("- ",event)