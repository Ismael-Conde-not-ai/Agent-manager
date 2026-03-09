class aIagentManager:
    from agent import AIagent
    
    def __init__(self):
        self.agentList=[]
    
    def add_agent(self, agent_x):
        '''
        adds agent created in main2
        '''
        self.agentList.append(agent_x)

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
                agent.autonomousStep()
                print(f"{agent.name} | Energy: {agent.energy} | Status: {agent.status}")