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

    def think(self,Idea):
        '''
        prints the agent's thoughts and what is willing to do
        '''
        print(Idea)
        return Idea
    
    def act(self):
        '''
        Spend energy to perform an action
        '''
        calcEnergy = self.energyCalculator
        energy = self.energy
        self.energy = calcEnergy('act',energy)
        print(f"El agente {self.name} esta actuando")

    def recharge(self):
        '''
        Recharges energy
        '''
        calcEnergy = self.energyCalculator
        energy = self.energy
        self.energy=calcEnergy("recharge",energy)

    def info(self):
        '''
        Prints agent's informationthin
        '''
        print(f"🤖 Agent: {self.name}\n 🎯 Goal: {self.goal}\n 🔋 Energy level: {self.energy}%\n 🏗️ Status: {self.status}")
