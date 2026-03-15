def rest (agent):
    '''
    In the agent object change the status to resting
    returns a (str) Agent is resting 
    '''
    agent.status = "resting"
    return "Agent rested"