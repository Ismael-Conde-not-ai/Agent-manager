class aIagentManager:
    from agent import AIagent
    from utils import showAndChoose
    def __init__(self):
        self.agentList=[]
    
    def createAgent(self):
        '''
        Defines name and goal of the agent then put it in the list, also creates a dictionary
        '''
        agents = self.AIagent
        name = str(input("ingrese el nombre del agente--->"))
        goal = str(input("ingrese el objetivo del agente--->"))
        newAgent = agents(name,goal)
        self.agentList.append(newAgent)
    
    def agentThink(self):
        '''
        Shows lis of agents and then makes the choice think.
        '''
        option =self.showAndChoose(self)
        self.agentList[option].think()
    
    def agentAction(self):
        '''
        Shows list of agents and then makes the choice act
        '''
        option =self.showAndChoose(self)
        self.agentList[option].act()
    
    def agentRecharge(self):
        '''
        Shows list of agents and then makes the choice recharge
        '''
        option =self.showAndChoose(self)
        self.agentList[option].recharge()

    def agentInformation(self):
        '''
        Shows list of agents and then show the choice information
        '''
        option = self.showAndChoose(self)
        self.agentList[option].info()

    def showAgentMemory (self):
        '''
        Shows the events memory of the agent
        '''
        option =self.showAndChoose(self)
        self.agentList[option].showMemory()

    def runSimulation (self,cycles):
        '''
        Runs a simulation of the agents determined for the cycles input
        '''
        if not self.agentList :
            print("No agents available")
            return
        for cycle in range(cycles):
            for agent in self.agentList:
                print(f"\n---Cycle {cycle + 1} ---")
                #agent.think()
                #agent.act()
                agent.autonomousStep()
                print(f"{agent.name} | Energy: {agent.energy} | Status: {agent.status}")
    
    def agentThinkAi (self):
        if not self.agentList :
            print("No agents available")
            return
        option = self.showAndChoose(self)
        self.agentList[option].thinkAi()