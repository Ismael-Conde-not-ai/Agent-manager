def work(agent):
    '''
    In the agent object it reduces energy by 20 and change the status to working
    returns a (str) Agent worked
    '''
    agent.energy -= 20
    agent.status = "working"

    return "Agent worked"