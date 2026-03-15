def recharge(agent):
    '''
    Changes the energy atribute of the agent object to (int)100,
    changes the status to recharged. If energy bigger than 100 energy = 100
    returns (str) The agent is recharged.
    '''
    agent.energy = 100
    agent.status = "recharging"

    if agent.energy > 100:
        agent.energy = 100

    return "Agent recharged"