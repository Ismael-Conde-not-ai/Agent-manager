class aIagentManager:
    from agent import AIagent
    from utils import showAndChoose
    def __init__(self):
        self.agentList=[]
        #self.agentListDictionary=[]
    
    def createAgent(self):
        '''
        Defines name and goal of the agent then put it in the list, also creates a dictionary
        '''
        agents = self.AIagent
        name = str(input("ingrese el nombre del agente--->"))
        goal = str(input("ingrese el objetivo del agente--->"))
        newAgent = agents(name,goal)
        self.agentList.append(newAgent)
        #self.agentListDictionary.append(vars(newAgent))
    
    def agentThink(self):
        option =self.showAndChoose(self)
        self.agentList[option].think()
    
    def agentAction(self):
        '''
        Show list of agents and then makes the choice act
        '''
        option =self.showAndChoose(self)
        self.agentList[option].act()
    
    def agentRecharge(self):
        '''
        Show list of agents and then makes the choice recharge
        '''
        option =self.showAndChoose(self)
        a=self.agentList[option]
        a.recharge()

    def agentInformation(self):
        '''
        Show list of agents and then show the choice information
        '''
        option = self.showAndChoose(self)
        self.agentList[option].info()

    def showAgentMemory (self):
        '''
        Shows the events memory of the agent
        '''
        option =self.showAndChoose(self)
        self.agentList[option].showMemory()