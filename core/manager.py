class Manager:
    from agents.agent import AIagent
    
    def __init__(self):
        self.agents={}
    
    def add_agent(self, agent):
        '''
        adds agent created in ...
        '''
        self.agents[agent.name] = agent

    def get_agent(self, name):
        '''
        returns agent object by name
        '''
        return self.agents.get(name)

    def list_agents(self):
        '''
        returns list of agent names
        '''
        return list(self.agents.keys())
